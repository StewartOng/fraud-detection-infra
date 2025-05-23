
output "api_url" {
  value = "${aws_api_gateway_deployment.prod.invoke_url}/check"
}


output "sns_topic" {
  value = aws_sns_topic.alerts.arn
}