import json
import boto3
import os
import uuid
from datetime import datetime

frauddetector = boto3.client('frauddetector')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

TABLE_NAME = os.environ['DDB_TABLE']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
DETECTOR_ID = os.environ['DETECTOR_ID']

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Determine check type based on input
        if 'email' in body and 'ipAddress' in body:
            # Email/IP fraud check
            return handle_email_ip_check(body)
        elif 'transactionId' in body or 'amount' in body:
            # Transaction fraud check
            return handle_transaction_check(body)
        else:
            raise ValueError("Invalid input - must include email/ip or transaction details")
            
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def handle_email_ip_check(body):
    email = body['email']
    ip_address = body['ipAddress']
    
    # Call Fraud Detector
    response = frauddetector.get_event_prediction(
        detectorId=DETECTOR_ID,
        eventId=str(uuid.uuid4()),
        eventTypeName='registration_event',
        eventTimestamp=datetime.now().isoformat(),
        entities=[{
            'entityType': 'customer',
            'entityId': email
        }],
        eventVariables={
            'email_address': email,
            'ip_address': ip_address
        }
    )
    
    outcome = response['ruleResults'][0]['outcomes'][0]
    
    # Store in DynamoDB
    table = dynamodb.Table(TABLE_NAME)
    table.put_item(Item={
        'checkId': str(uuid.uuid4()),
        'type': 'email_ip_check',
        'email': email,
        'ipAddress': ip_address,
        'outcome': outcome,
        'timestamp': datetime.now().isoformat()
    })
    
    # Send alert if fraud
    if outcome == 'fraud':
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='🚨 Fraud Detected - Suspicious Registration',
            Message=f"Fraud detected:\nEmail: {email}\nIP: {ip_address}"
        )
    
    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'outcome': outcome})
    }

def handle_transaction_check(body):
    transaction = {
        'transactionId': body.get('transactionId', str(uuid.uuid4())),
        'customerId': body.get('customerId', 'anonymous'),
        'amount': float(body.get('amount', 0)),
        'ipAddress': body.get('ipAddress', '')
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
        'timestamp': datetime.now().isoformat(),
        'type': 'transaction_check'
    })

    # Send alert if fraud
    if outcome == 'fraud':
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='⚠️ Fraud Alert - Suspicious Transaction',
            Message=json.dumps({
                'TransactionID': transaction['transactionId'],
                'CustomerID': transaction['customerId'],
                'Amount': transaction['amount'],
                'IP': transaction['ipAddress']
            })
        )

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({
            'transactionId': transaction['transactionId'],
            'outcome': outcome
        })
    }


