
import boto3
import uuid
import json
from datetime import datetime

# Create the Fraud Detector client
client = boto3.client('frauddetector', region_name='us-east-1')  # use the correct region

# Replace these with the exact values used in my AWS Console setup
# Construct a test prediction event
# Make Sure in the AWS Console You Have for example
# Detector created: stewart-detector
# Event type created: transaction_event
# Entity type: customer
# Variables:
# transaction_amount (number or string type)
# email_address (string)
# ip_address (string)
# Model trained and version active
# At least one rule using the created model to return an outcome (fraud, legit, etc.)

response = client.get_event_prediction(
    detectorId="detector_getting_started",
    eventId=str(uuid.uuid4()),
    eventTypeName="registration",
    eventTimestamp="2024-05-04T10:00:00Z",
    entities=[{"entityType": "customer", "entityId": str(uuid.uuid4())}],
    eventVariables={
        "email_address": "fake_acostsusan@example.org",
        "ip_address": "46.41.252.160"
    }
)

# Output the predicted outcome

print('Predicted outcome:', json.dumps(response['ruleResults'][0]['outcomes']))
