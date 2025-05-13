locals {
  lambda_instance_reservation_alerter_function_name = "instance_reservation_alerter"
}


module "instance_reservation_alerter" {

  source = "github.com/wearetechnative/terraform-aws-lambda.git?ref=66c495f917207c64c67fe15ef2141483bc3a567c"

  name              = local.lambda_instance_reservation_alerter_function_name
  role_arn          = module.instance_reservation_alerter_lambda_role.role_arn
  role_arn_provided = true

  handler                   = "lambda_function.lambda_handler"
  source_type               = "local"
  source_directory_location = "${path.module}/lambda_instance_reservation_alerter"
  source_file_name          = null

  kms_key_arn = var.kms_key_arn
  sqs_dlq_arn = var.sqs_dlq_arn
  memory_size = 128
  timeout     = 300
  runtime     = "python3.9"

  environment_variables = {
    CLIENT_NAME            = var.client_name
    ACCOUNT_NAME           = var.account_name
    NOTIFICATION_ENDPOINTS = jsonencode(var.notification_endpoints)
  }
}

# Cron job event rule directly tied to lambda function.
resource "aws_cloudwatch_event_rule" "refresh_reservation_alerter" {
  name        = "trigger-reservation-alerter-rule"
  description = "Trigger reservation alerter lambda every 24 hours."

  state               = "ENABLED"
  event_bus_name      = "default"
  schedule_expression = "rate(24 hours)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule           = aws_cloudwatch_event_rule.refresh_reservation_alerter.id
  event_bus_name = aws_cloudwatch_event_rule.refresh_reservation_alerter.event_bus_name

  arn = module.instance_reservation_alerter.lambda_function_arn

  dead_letter_config {
    arn = var.sqs_dlq_arn
  }
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id_prefix = module.instance_reservation_alerter.lambda_function_name
  action              = "lambda:InvokeFunction"
  function_name       = module.instance_reservation_alerter.lambda_function_name
  principal           = "events.amazonaws.com"
  source_arn          = aws_cloudwatch_event_rule.refresh_reservation_alerter.arn
}

module "instance_reservation_alerter_lambda_role" {

  source = "github.com/wearetechnative/terraform-aws-iam-role.git?ref=9229bbd0280807cbc49f194ff6d2741265dc108a"

  role_name = "lambda_instance_reservation_alerter_lambda_role"

  aws_managed_policies = []
  customer_managed_policies = {
    "sqs_observability_receiver" : jsondecode(data.aws_iam_policy_document.sqs_observability_receiver.json)
    "allow_sns_publish" : jsondecode(data.aws_iam_policy_document.allow_sns_publish.json)
    "read_reservations" : jsondecode(data.aws_iam_policy_document.read_reservations.json)
  }

  trust_relationship = {
    "lambda" : { "identifier" : "lambda.amazonaws.com", "identifier_type" : "Service", "enforce_mfa" : false, "enforce_userprincipal" : false, "external_id" : null, "prevent_account_confuseddeputy" : false }
  }
}

data "aws_iam_policy_document" "sqs_observability_receiver" {
  statement {
    sid = "SQSObservabilityReceiver"

    actions = ["sqs:SendMessage"]

    resources = [var.tn_master_observability_receiver_sqs_arn]
  }
}

data "aws_iam_policy_document" "allow_sns_publish" {
  statement {
    sid = "AllowSNSPublish"

    actions = ["sns:Publish"]

    resources = ["arn:aws:sns:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"]
  }
}

data "aws_iam_policy_document" "read_reservations" {
  statement {
    sid = "DescribeReservations"

    actions = ["rds:DescribeReservedDBInstances",
      "ec2:DescribeHostReservations",
      "ec2:DescribeReservedInstances",
      "ec2:DescribeCapacityReservations",
    "redshift:DescribeReservedNodes"]

    resources = ["*"]
  }
}
