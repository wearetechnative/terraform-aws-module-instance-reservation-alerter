# Example

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
