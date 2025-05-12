locals {
  lambda_instance_reservation_alerter_function_name = "instance_reservation_alerter"
}


module "instace_reservation_alerter" {
    source = "github.com/wearetechnative/terraform-aws-lambda.git?ref=66c495f917207c64c67fe15ef2141483bc3a567c"
    
  name              = local.lambda_instance_reservation_alerter_function_name
  role_arn          = module.instance_reservation_alerter_lambda_role.role_arn
  role_arn_provided = true

  handler                   = "lambda_function.lambda_handler"
  source_type               = "local"
  source_directory_location = "${path.module}/lambda_instace_reservation_alerter"
  source_file_name          = null

  kms_key_arn = var.kms_key_arn
  sqs_dlq_arn = var.sqs_dlq_arn
  memory_size = 128
  timeout     = 300
  runtime     = "python3.9"

  environment_variables = {
    
  }
}

module "instance_reservation_alerter_lambda_role" {
  source = "github.com/wearetechnative/terraform-aws-iam-role.git?ref=9229bbd0280807cbc49f194ff6d2741265dc108a"

  role_name = "lambda_instance_reservation_alerter_lambda_role"

  aws_managed_policies = []
  customer_managed_policies = {
    "sqs_observability_receiver" : jsondecode(data.aws_iam_policy_document.sqs_observability_receiver.json)
  }

  trust_relationship = {
    "lambda" : { "identifier" : "lambda.amazonaws.com", "identifier_type" : "Service", "enforce_mfa" : false, "enforce_userprincipal" : false, "external_id" : null, "prevent_account_confuseddeputy" : false }
  }
}

data "aws_iam_policy_document" "example" {
  statement {
    sid = "example"

    actions = ["example:example"]

    resources = ["*"]
  }
}
