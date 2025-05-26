variable "region" {
  default = "us-east-1"
}

variable "alert_email" {
  description = "Email to receive fraud alerts"
  type        = string
}

variable "dynamodb_table" {
  default = "fraud-transactions"
}

variable "detector_name" {
  description = "Name of your Fraud Detector"
  type        = string
}
