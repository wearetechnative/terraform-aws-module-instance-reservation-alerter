import json
import os

## Any OS environment that you need to use.
os.environ['AWS_PARTITION'] = "aws"
os.environ['AWS_MONITORING_ACCOUND_ID'] = "862764382109"

# Imports the Lambda function code
from lambda_function import *

# Lambda context object to retrieve Python function information
# You can leave as is or update it to fit your needs.
class LambdaContext():
    aws_request_id='f3090957-185e-4719-a144-83f813f05bba'
    log_group_name='/aws/lambda/service_quota_alerter'
    log_stream_name='2022/10/10/[$LATEST]6b4976d7c5f54d7d8186dddc7dec210a'
    function_name='service_quota_alerter'
    memory_limit_in_mb=128
    function_version='$LATEST'
    invoked_function_arn='arn:aws:lambda:eu-west-1:289386199983:function:service_quota_alerter'
    client_context='None'

# This is the name or file of the test event that you want to use.
f = open("lambda_test_event.json", "r")
event = json.loads(f.read()) # can be any event since this Lambda is triggered by EventBridge
f.close()

lambda_handler(event, LambdaContext())
