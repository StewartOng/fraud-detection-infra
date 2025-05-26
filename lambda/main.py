import boto3
import os
import json
import uuid
from datetime import datetime

frauddetector = boto3.client('frauddetector')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

DETECTOR_ID = os.environ['DETECTOR_ID']
DDB_TABLE = os.environ['DDB_TABLE']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    try:
        print("Received event:", event)

        ip = event.get('ipAddress')
        email = event.get('email')
        amount = event.get('amount', '100')
        user_id = event.get('userId', 'guest')

        transaction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        prediction = frauddetector.get_event_prediction(
            detectorId=DETECTOR_ID,
            eventId=transaction_id,
            eventTypeName='transaction_event',
            eventTimestamp=timestamp,
            entities=[{'entityType': 'customer', 'entityId': user_id}],
            eventVariables={
                'ip_address': ip,
                'email_address': email,
                'transaction_amount': str(amount)
            }
        )

        outcome = prediction['ruleResults'][0]['outcomes'][0]
        print("Fraud outcome:", outcome)

        # Store in DynamoDB
        table = dynamodb.Table(DDB_TABLE)
        table.put_item(Item={
            'transactionId': transaction_id,
            'userId': user_id,
            'email': email,
            'ip': ip,
            'amount': amount,
            'outcome': outcome,
            'timestamp': timestamp
        })

        # Send alert if fraudulent
        if outcome.lower() == 'fraud':
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="⚠️ Fraud Alert",
                Message=f"Fraud detected!\nTransaction ID: {transaction_id}\nEmail: {email}\nIP: {ip}"
            )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'transactionId': transaction_id,
                'outcome': outcome
            })
        }

    except Exception as e:
        print("Error:", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
