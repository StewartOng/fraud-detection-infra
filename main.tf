terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.44.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# SNS Alerts
resource "aws_sns_topic" "alerts" {
  name = "fraud-alerts"
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# DynamoDB Table
resource "aws_dynamodb_table" "transactions" {
  name         = var.dynamodb_table
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "transactionId"

  attribute {
    name = "transactionId"
    type = "S"
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_exec" {
  name = "lambda-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policies" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_role_policy_attachment" "fraud_detector_permissions" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonFraudDetectorFullAccess"
}

# Lambda Function
resource "aws_lambda_function" "fraud_checker" {
  filename         = "${path.module}/lambda/fraud_predictor.zip"
  function_name    = "fraud-checker"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = filebase64sha256("${path.module}/lambda/fraud_predictor.zip")

  environment {
    variables = {
      DDB_TABLE      = var.dynamodb_table
      SNS_TOPIC_ARN  = aws_sns_topic.alerts.arn
      DETECTOR_ID    = var.detector_name   # ← reference only; not managed in Terraform
    }
  }
}


