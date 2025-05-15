# Terraform AWS instance reservation alerter ![](https://img.shields.io/github/actions/workflow/status/wearetechnative/terraform-aws-module-instance-reservation-alerter/tflint.yaml?style=plastic)

![](https://img.shields.io/github/actions/workflow/status/wearetechnative/terraform-aws-module-instance-reservation-alerter/tflint.yaml?style=plastic)

<!-- SHIELDS -->


This module implements a lambda that monitors AWS reserved instances every 24 hours across multiple services and alerts when they're about to expire.
The Lambda prevents unexpected cost increases by alerting teams when reserved instances are nearing expiration, allowing time to renew or adjust resources.

[![technative_logo](we-are-technative.png)](https://www.technative.nl)

## How does it work

1. Collect Reservation Data:

   - Queries across multiple AWS services (RDS, RedShift, EC2)
   - Filters for active reservations only
   - Standardizes reservation information into a common format

2. Check Expiration Timeframes:

   - Calculates days remaining until reservation expiry
   - Flags reservations with critical timeframes (7 days and 1 day)
   - Assigns priority levels (P2 for 7 days, P1 for 1 day)

3. Send Notifications:

   - Determines notification method based on endpoint configuration
   - For SNS: Sends formatted alerts to SNS topics
   - For SQS: Creates structured JSON messages for queue processing

4. Handle Errors:

   - Captures exceptions with full traceback information
   - Creates formatted error messages for logging
   - Raises exceptions for Lambda monitoring

### First use after you clone this repository or when .pre-commit-config.yaml is updated

Run `pre-commit install` to install any guardrails implemented using pre-commit.

See [pre-commit installation](https://pre-commit.com/#install) on how to install pre-commit.

...

## Usage

To use this module ...

```hcl

module "reservation_alerter" {

    source = "github.com/wearetechnative/terraform-aws-module-instance-reservation-alerter.git?ref=f7856e6288ac2cd41362bc085cf2a7fdeb683a99"

    sqs_dlq_arn    = sqs.dlq.arn
    kms_key_arn    = kms.default_key.arn

    client_name  = "ClientName"
    account_name = "Production"

    notification_endpoints = ["https://sqs.eu-central-1.amazonaws.com/123455677/sqs_name", aws_sns_topic.observability.arn]
}

```

<!-- BEGIN_TF_DOCS -->
<!-- END_TF_DOCS -->
