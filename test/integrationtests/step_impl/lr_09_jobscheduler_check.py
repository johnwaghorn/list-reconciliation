import base64
import json
import os

import boto3
from getgauge.python import Messages, data_store, step

from .lr_03_dynamodb import get_latest_jobid
from .test_helpers import PDS_API_ENV
from .tf_aws_resources import get_terraform_output

REGION_NAME = "eu-west-2"
LR_09_LAMBDA_ARN = get_terraform_output("lr_09_lambda")
LR_13_BUCKET = get_terraform_output("lr_13_bucket")
ROOT = os.path.dirname(os.path.abspath(__file__))
EXPECTED_GP_ONLY_DATA = os.path.join(ROOT, "data", PDS_API_ENV)

s3 = boto3.client("s3", REGION_NAME)
lambda_ = boto3.client("lambda", REGION_NAME)


@step("trigger lr09 and expected statuscode is <expstatuscode>")
def trigger_lr09(expstatuscode):

    response = lambda_.invoke(
        FunctionName=LR_09_LAMBDA_ARN, LogType="Tail", Payload=json.dumps({})
    )
    for key, _ in response.items():
        if key == "ResponseMetadata":
            assert response["ResponseMetadata"]["HTTPStatusCode"] == int(expstatuscode)


@step("trigger lr09 and ensure scheduled checked successfully completed")
def trigger_lr09_get_requestid():
    expected_job_id = get_latest_jobid()

    response = lambda_.invoke(
        FunctionName=LR_09_LAMBDA_ARN, LogType="Tail", Payload="{}"
    )
    for key, _ in response.items():
        if key == "ResponseMetadata":
            tail_output = base64.b64decode(
                response["ResponseMetadata"]["HTTPHeaders"]["x-amz-log-result"]
            )
            log_output = tail_output.decode("utf-8")
            expected_line = f"Updated JobStatus for jobId='{expected_job_id}'"

            try:
                log_output.index(expected_line)
                Messages.write_message("LR-09 scheduled check sucessfully completed")
            except ValueError:
                Messages.write_message("LR-09 scheduled check unsuccessful")

    data = json.loads(response["Payload"].read())
    data_store.scenario["lr_09"] = {"lr_09_data": data}

    actual_job_id = data_store.scenario["lr_09"]["lr_09_data"]["processed_jobs"][0]
    assert expected_job_id == actual_job_id
