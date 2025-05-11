# lambda/handler.py
import json
import boto3
import uuid
import os
from datetime import datetime

frauddetector = boto3.client('frauddetector', region_name='us-east-1')
sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

DETECTOR_ID = os.environ['DETECTOR_ID']
DDB_TABLE = os.environ['DDB_TABLE']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    email = event.get("email_address")
    ip = event.get("ip_address")

    if not email or not ip:
        return {
            "statusCode": 400,
            "body": "Missing 'email_address' or 'ip_address'"
        }

    prediction = frauddetector.get_event_prediction(
        detectorId=DETECTOR_ID,
        eventId=str(uuid.uuid4()),
        eventTypeName="registration",
        eventTimestamp=datetime.utcnow().isoformat() + "Z",
        entities=[{
            "entityType": "customer",
            "entityId": str(uuid.uuid4())
        }],
        eventVariables={
            "email_address": email,
            "ip_address": ip
        }
    )

    outcome = prediction['ruleResults'][0]['outcomes'][0]

    # Optional: Log to DynamoDB
    table = dynamodb.Table(DDB_TABLE)
    table.put_item(Item={
        "transactionId": str(uuid.uuid4()),
        "email": email,
        "ip": ip,
        "outcome": outcome,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Alert via SNS if fraud
    if outcome == "fraud":
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="🚨 Fraud Detected!",
            Message=f"Suspicious activity detected.\nEmail: {email}\nIP: {ip}"
        )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "email": email,
            "ip": ip,
            "outcome": outcome
        })
    }
