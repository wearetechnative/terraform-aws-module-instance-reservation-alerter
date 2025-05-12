# Instance Reservation Alerter

The Lambda prevents unexpected cost increases by alerting teams when reserved instances are nearing expiration, allowing time to renew or adjust resources.

## Assignment details

- Add eventbridge rule that runs every 24 hours.
- Eventbridge rule should trigger lambda.
- Add trigger to run Lambda if code is changed.
- Create SNS topic if client is not managed services and if client is managed services do not create SNS topic.
- Update Lambda role to be able to publish sns message.
