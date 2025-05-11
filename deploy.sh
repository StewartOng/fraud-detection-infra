#!/bin/bash

set -e

echo "📦 Zipping Lambda function..."
cd lambda
zip -r fraud_predictor.zip handler.py > /dev/null
cd ..

echo "🚀 Running Terraform..."
cd terraform
terraform init -upgrade
terraform plan -out=tfplan
terraform apply tfplan
