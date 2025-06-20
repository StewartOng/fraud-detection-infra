terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

resource "aws_sns_topic" "alerts" {
  name = "fraud-alerts"
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_dynamodb_table" "transactions" {
  name         = var.dynamodb_table
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "transactionId"

  attribute {
    name = "transactionId"
    type = "S"
  }
}

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

resource "aws_iam_policy" "lambda_sns_publish" {
  name        = "lambda-sns-publish-policy"
  description = "Allow Lambda to publish to SNS topic"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "sns:Publish",
        Effect   = "Allow",
        Resource = aws_sns_topic.alerts.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_lambda_sns" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_sns_publish.arn
}

resource "aws_iam_role_policy_attachment" "lambda_policies" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "fraud_checker" {
  filename         = "${path.module}/lambda/fraud_predictor.zip"
  function_name    = "fraud-checker"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "main.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = filebase64sha256("${path.module}/lambda/fraud_predictor.zip")

  environment {
    variables = {
      DDB_TABLE      = var.dynamodb_table
      SNS_TOPIC_ARN  = aws_sns_topic.alerts.arn
      DETECTOR_ID    = var.detector_name
    }
  }
}

resource "aws_iam_policy" "fraud_detector_policy" {
  name        = "CustomFraudDetectorPolicy"
  description = "Custom policy for Amazon Fraud Detector access"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = ["frauddetector:GetEventPrediction"],
      Resource = "*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "attach_fraud_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.fraud_detector_policy.arn
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/fraud-checker"
  retention_in_days = 7
}
