#!/bin/bash

# CONFIG
DETECTOR_ID="transaction-detector"
ENTITY_TYPE="customer"
EVENT_TYPE="transaction_event"
RULE_ID="default-rule"
OUTCOME_NAME="fraud"
OUTCOME_NAME_2="legit"

# 1. Create entity type
aws frauddetector create-entity-type \
  --name "$ENTITY_TYPE"

# 2. Create variables
aws frauddetector create-variable --name transactionId --data-type STRING --data-source EVENT --default-value "unknown" --variable-type TRANSACTION
aws frauddetector create-variable --name customerId    --data-type STRING --data-source EVENT --default-value "unknown" --variable-type CUSTOMER
aws frauddetector create-variable --name amount        --data-type FLOAT  --data-source EVENT --default-value "0.0"     --variable-type PRICE
aws frauddetector create-variable --name ipAddress     --data-type STRING --data-source EVENT --default-value "0.0.0.0" --variable-type IP_ADDRESS

# 3. Create event type
aws frauddetector create-event-type \
  --name "$EVENT_TYPE" \
  --event-variables transactionId customerId amount ipAddress \
  --entity-types "$ENTITY_TYPE" \
  --labels "$OUTCOME_NAME" "$OUTCOME_NAME_2"

# 4. Create outcomes
aws frauddetector create-outcome --name "$OUTCOME_NAME"
aws frauddetector create-outcome --name "$OUTCOME_NAME_2"

# 5. Create detector + rule
aws frauddetector create-detector \
  --detector-id "$DETECTOR_ID" \
  --event-type-name "$EVENT_TYPE"

aws frauddetector create-rule \
  --rule-id "$RULE_ID" \
  --detector-id "$DETECTOR_ID" \
  --expression "amount > 5000" \
  --language DETECTORPL \
  --outcomes "$OUTCOME_NAME"

# 6. Create and deploy detector version
aws frauddetector create-detector-version \
  --detector-id "$DETECTOR_ID" \
  --rules "ruleId=$RULE_ID,detectorId=$DETECTOR_ID,ruleVersion=1.0" \
  --rule-execution-mode FIRST_MATCHED

aws frauddetector update-detector-version-status \
  --detector-id "$DETECTOR_ID" \
  --detector-version-id "1" \
  --status ACTIVE

echo "✅ Fraud Detector setup complete"