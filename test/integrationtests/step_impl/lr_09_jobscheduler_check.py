from getgauge.python import step, Messages
import boto3
import json
import os
import base64

from utils.datetimezone import get_datetime_now
from .tf_aws_resources import get_aws_resources

# On github
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)

REGION_NAME = "eu-west-2"
AWS_RESOURCE = get_aws_resources()
LR_09_LAMBDA_ARN = AWS_RESOURCE["lr_09_lambda"]["value"]


@step("trigger lr09 and expected statuscode is <expstatuscode>")
def trigger_lr09(expstatuscode):
    client = dev.client("lambda", REGION_NAME)
    response = client.invoke(FunctionName=LR_09_LAMBDA_ARN, LogType="Tail", Payload=json.dumps({}))
    for key, value in response.items():
        if key == "ResponseMetadata":
            assert response["ResponseMetadata"]["HTTPStatusCode"] == int(expstatuscode)


@step("trigger lr09 and ensure scheduled checked successfully completed")
def trigger_lr09_get_requestid():
    client = dev.client("lambda", REGION_NAME)
    response = client.invoke(FunctionName=LR_09_LAMBDA_ARN, LogType="Tail", Payload=json.dumps({}))

    for key, value in response.items():
        if key == "ResponseMetadata":
            request_id = response["ResponseMetadata"]["RequestId"]
            tail_output = base64.b64decode(
                response["ResponseMetadata"]["HTTPHeaders"]["x-amz-log-result"]
            )
            log_output = tail_output.decode("utf-8")
            expected_line = "Scheduled checked successfully completed"

            try:
                log_output.index(expected_line)
            except ValueError:
                Messages.write_message("LR-09 scheduled check Unsucessfull")
            else:
                Messages.write_message("LR-09 scheduled check sucessfully completed")

        return request_id
