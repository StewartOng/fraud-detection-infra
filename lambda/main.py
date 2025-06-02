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
        print("Received event (ignored in test mode):", event)

        # ✅ HARDCODED TEST INPUTS
        ip_address = "46.41.252.160"
        email_address = "fake_acostasusan@example.org"
        user_id = "test-user"

        transaction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        print("Calling Fraud Detector with:")
        print(f"  IP Address: {ip_address}")
        print(f"  Email Address: {email_address}")
        print(f"  User ID: {user_id}")
        print(f"  Detector ID: {DETECTOR_ID}")
        print(f"  Timestamp: {timestamp}")

        prediction = frauddetector.get_event_prediction(
            detectorId=DETECTOR_ID,
            eventId=transaction_id,
            eventTypeName='new_registration',
            eventTimestamp=timestamp,
            entities=[{'entityType': 'customer', 'entityId': user_id}],
            eventVariables={
                'ip_address': ip_address,
                'email_address': email_address,
            }
        )

        print("Full prediction response:", json.dumps(prediction, indent=2))

        rule_results = prediction.get('ruleResults', [])
        if not rule_results or not rule_results[0].get('outcomes'):
            outcome = "unknown"
            print("No outcome found in prediction, defaulting to 'unknown'")
        else:
            outcome = rule_results[0]['outcomes'][0]
        
        print("Fraud outcome:", outcome)

        # ✅ Store in DynamoDB
        table = dynamodb.Table(DDB_TABLE)
        item = {
            'transactionId': transaction_id,
            'userId': user_id,
            'email': email_address,
            'ip': ip_address,
            'outcome': outcome,
            'timestamp': timestamp
        }

        response = table.put_item(Item=item)
        print("DynamoDB put_item response:", response)

        # ✅ Send alert if outcome is suspicious
        suspicious_outcomes = ['fraud', 'high_risk_customer']
        if outcome.lower() in suspicious_outcomes:
            print("Sending fraud alert via SNS...")
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="⚠️ Fraud Alert: New Account Registration",
                Message=(
                    f"Fraud detected!\n\n"
                    f"Transaction ID: {transaction_id}\n"
                    f"Outcome: {outcome}\n"
                    f"Email Address: {email_address}\n"
                    f"IP Address: {ip_address}\n"
                    f"Timestamp: {timestamp}"
                )
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
