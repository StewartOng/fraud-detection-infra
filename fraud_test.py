import boto3, uuid, json
from datetime import datetime

client = boto3.client('frauddetector', region_name='us-east-1')  # Match your detector's region

response = client.get_event_prediction(
    detectorId="group3_fraud_detector",  # Make sure this ID exists and is active
    eventId=str(uuid.uuid4()),
    eventTypeName="registration",
    eventTimestamp=datetime.utcnow().isoformat() + "Z",  # ← Proper ISO timestamp
    entities=[{"entityType": "customer", "entityId": str(uuid.uuid4())}],
    eventVariables={
        "email_address": "fake_acostsusan@example.org",
        "ip_address": "46.41.252.160"
    }
)

print('The predicted outcome is: ' + json.dumps(response['ruleResults'][0]['outcomes']))
