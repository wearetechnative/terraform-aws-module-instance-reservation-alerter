# VARIABLES

variable "tn_master_observability_receiver_sqs_arn" {
  description = "SQS queue arn of the central observability hub of TechNative"
  type        = string
  default     = "arn:aws:sqs:eu-central-1:611159992020:sqs-opsgenie-lambda-queue-20220711145511259200000002"
}

variable "sqs_dlq_arn" {
  description = "SQS DLQ ARN for any messages / events that fail to process."
  type        = string
}

variable "kms_key_arn" {
  description = "KMS CMK used for any on-disk encryption supported."
  type        = string
}

variable "client_name" {
  description = "Name of the Client"
  default     = "Technative_LandingZone"
}

variable "account_name" {
  description = "Name of the account."
  default     = "Unknown"
}

variable "notification_endpoints" {
  description = "List of SNS topic ARN or SQS queue URL."
  type        = list(string)
}