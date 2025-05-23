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

# Add this after your existing resources
resource "aws_api_gateway_rest_api" "fraud_api" {
  name        = "fraud-detection-api"
  description = "API for fraud detection"
}

resource "aws_api_gateway_resource" "check" {
  rest_api_id = aws_api_gateway_rest_api.fraud_api.id
  parent_id   = aws_api_gateway_rest_api.fraud_api.root_resource_id
  path_part   = "check"
}

resource "aws_api_gateway_method" "post" {
  rest_api_id   = aws_api_gateway_rest_api.fraud_api.id
  resource_id   = aws_api_gateway_resource.check.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id             = aws_api_gateway_rest_api.fraud_api.id
  resource_id             = aws_api_gateway_resource.check.id
  http_method             = aws_api_gateway_method.post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.fraud_checker.invoke_arn
}

resource "aws_api_gateway_deployment" "prod" {
  depends_on  = [aws_api_gateway_integration.lambda]
  rest_api_id = aws_api_gateway_rest_api.fraud_api.id
  stage_name  = "prod"
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fraud_checker.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.fraud_api.execution_arn}/*/*"
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

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


# Lambda Function
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
      DETECTOR_ID    = var.detector_name   # ← reference only; not managed in Terraform
    }
  }
}

resource "aws_iam_policy" "fraud_detector_policy" {
  name        = "CustomFraudDetectorPolicy"
  description = "Custom policy for Amazon Fraud Detector access"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "frauddetector:GetEventPrediction",
   
        ],
        Resource = "*"
      }
    ]
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