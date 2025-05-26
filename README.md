# fraud-detection-infra

<b> High level Architecture Diagram </b>

![alt text](image-1.png)
![alt text](highleveldiagram.png)

<b>Program Structure Explanation</b>

<b>1. Frontend (App.tsx)</b>

<b>Purpose</b>: Provides a user interface for submitting transaction details for fraud detection.

<b>Key Features</b>:

Form with inputs for Transaction ID, Customer ID, Amount, and IP Address

Submit button that sends data to the backend API

Displays the fraud detection result

<b>Technologies</b>: React, TypeScript, Axios for API calls

<b> 2. Lambda Functions </b>

<b> 2.1 handler.py</b>

<b>Purpose</b>: Handles fraud detection requests for registration events.

<b>Key Features</b>:

Receives email and IP address as input

Calls Amazon Fraud Detector API for prediction

Logs results to DynamoDB

Sends SNS alerts for fraudulent events

<b>AWS Services Used</b>: Fraud Detector, DynamoDB, SNS

<b>2.2 main.py</b>

<b>Purpose</b>: Handles fraud detection for financial transactions.

<b>Key Features</b>:

Receives transaction details (ID, customer, amount, IP)

Calls Fraud Detector with transaction variables

Stores results in DynamoDB

Triggers SNS alerts for fraud cases

<b>AWS Services Used</b>: Fraud Detector, DynamoDB, SNS

<b>3. Infrastructure (Terraform)</b>

<b>3.1 main.tf</b>

<b>Purpose</b>: Defines and provisions the AWS infrastructure.

<b>Key Components</b>:

SNS Topic for fraud alerts with email subscription

DynamoDB table for transaction storage

IAM role with permissions for Lambda

Lambda function configuration

<b>AWS Services Provisioned</b>: SNS, DynamoDB, IAM, Lambda

<b>3.2 variables.tf</b>

Purpose: Defines configurable variables for the Terraform deployment.

Key Variables:

AWS region

Alert email address

DynamoDB table name

Fraud Detector name

<b>3.3 outputs.tf</b>

<b>Purpose</b>: Outputs important resource information after deployment.

<b>Outputs</b>: SNS Topic ARN



<b>4. Fraud Detector Configuration</b>


Entity Type: "customer"

Event Type: "transaction_event"

Variables:

transactionId (STRING)

customerId (STRING)

ipAddress (STRING)

Rule: Flags transactions over $5000 as potential fraud

Outcomes: "fraud" or "legit"

<b>Workflow</b>

User submits transaction details through React frontend

API Gateway receives the request and triggers Lambda function

Lambda function:

Sends transaction data to Fraud Detector

Receives fraud prediction outcome

Stores transaction and result in DynamoDB

Sends alert via SNS if fraud is detected

Result is returned to the frontend for display

<b>Key AWS Services Integration</b>

<b>Amazon Fraud Detector</b>: Core fraud detection service

<b>Lambda</b>: Serverless compute for business logic

<b>API Gateway</b>: Frontend-to-backend interface

<b>DynamoDB</b>: Transaction history storage

<b>SNS</b>: Fraud alert notifications

<b>IAM</b>: Security and permissions management

This architecture provides a scalable, serverless solution for real-time fraud detection with alerting and audit capabilities.