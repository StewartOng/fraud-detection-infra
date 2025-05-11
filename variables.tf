

variable "region" {
  default = "us-east-1"
}

variable "alert_email" {
  description = "The email address for fraud alerts"
}

variable "dynamodb_table" {
  default = "transactions"
}

variable "detector_name" {
  description = "Name of the existing Fraud Detector created via Console"
  type        = string
  default     = "detector_getting_started"
}
