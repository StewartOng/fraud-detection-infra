import json
import boto3
import os
from datetime import datetime

frauddetector = boto3.client('frauddetector')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

TABLE_NAME = os.environ['DDB_TABLE']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
DETECTOR_ID = os.environ['DETECTOR_ID']

def lambda_handler(event, context):
    # Parse input from API Gateway
    try:
        body = json.loads(event['body'])
        transaction = {
            'transactionId': body.get('transactionId', str(uuid.uuid4())),
            'customerId': body.get('customerId', ''),
            'amount': float(body.get('amount', 0)),
            'ipAddress': body.get('ipAddress', '')
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid input'})
        }

    # Call Fraud Detector
    result = frauddetector.get_event_prediction(
        detectorId=DETECTOR_ID,
        eventId=transaction['transactionId'],
        eventTypeName='transaction_event',
        eventTimestamp=datetime.now().isoformat(),
        entities=[{
            'entityType': 'customer',
            'entityId': transaction['customerId']
        }],
        eventVariables={
            'transactionId': transaction['transactionId'],
            'customerId': transaction['customerId'],
            'amount': str(transaction['amount']),
            'ipAddress': transaction['ipAddress']
        }
    )

    outcome = result['ruleResults'][0]['outcomes'][0]

    # Store in DynamoDB
    table = dynamodb.Table(TABLE_NAME)
    table.put_item(Item={
        'transactionId': transaction['transactionId'],
        'customerId': transaction['customerId'],
        'amount': transaction['amount'],
        'ipAddress': transaction['ipAddress'],
        'outcome': outcome,
        'timestamp': datetime.now().isoformat()
    })

    # Send SNS alert if fraud
    if outcome == 'fraud':
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='⚠️ Fraud Alert',
            Message=json.dumps({
                'TransactionID': transaction['transactionId'],
                'CustomerID': transaction['customerId'],
                'Amount': transaction['amount'],
                'IP': transaction['ipAddress']
            })
        )

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'transactionId': transaction['transactionId'],
            'outcome': outcome
        })
    }


