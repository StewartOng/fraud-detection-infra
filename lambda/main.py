import json
import boto3
import os

frauddetector = boto3.client('frauddetector')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

TABLE_NAME = os.environ['DDB_TABLE']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
DETECTOR_ID = os.environ['DETECTOR_ID']

def lambda_handler(event, context):
    transaction = event['transaction']
    result = frauddetector.get_event_prediction(
        detectorId=DETECTOR_ID,
        eventId=transaction['transactionId'],
        eventTypeName='transaction_event',
        eventTimestamp=context.aws_request_id,
        eventVariables={
            'transactionId': transaction['transactionId'],
            'customerId': transaction['customerId'],
            'amount': str(transaction['amount']),
            'ipAddress': transaction['ipAddress']
        }
    )

    outcome = result['ruleResults'][0]['outcomes'][0]

    table = dynamodb.Table(TABLE_NAME)
    table.put_item(Item={
        'transactionId': transaction['transactionId'],
        'customerId': transaction['customerId'],
        'amount': transaction['amount'],
        'ipAddress': transaction['ipAddress'],
        'outcome': outcome
    })

    if outcome == 'fraud':
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='⚠️ Fraud Alert',
            Message=json.dumps(transaction)
        )

    return {
        'statusCode': 200,
        'body': json.dumps({'outcome': outcome})
    }