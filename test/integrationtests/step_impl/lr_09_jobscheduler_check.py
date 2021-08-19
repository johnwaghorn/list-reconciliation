from getgauge.python import step, Messages, data_store
from .tf_aws_resources import get_terraform_output
from .lr_03_dynamodb import get_latest_jobid
from .test_helpers import PDS_API_ENV

import boto3
import json
import os
import base64

REGION_NAME = "eu-west-2"
LR_09_LAMBDA_ARN = get_terraform_output("lr_09_lambda")
LR_13_BUCKET = get_terraform_output("lr_13_bucket")
ROOT = os.path.dirname(os.path.abspath(__file__))
EXPECTED_GP_ONLY_DATA = os.path.join(ROOT, "data", PDS_API_ENV)

s3 = boto3.client("s3", REGION_NAME)


@step("trigger lr09 and expected statuscode is <expstatuscode>")
def trigger_lr09(expstatuscode):
    client = boto3.client("lambda", REGION_NAME)
    response = client.invoke(FunctionName=LR_09_LAMBDA_ARN, LogType="Tail", Payload=json.dumps({}))
    for key, value in response.items():
        if key == "ResponseMetadata":
            assert response["ResponseMetadata"]["HTTPStatusCode"] == int(expstatuscode)


@step("trigger lr09 and ensure scheduled checked successfully completed")
def trigger_lr09_get_requestid():
    expected_job_id = get_latest_jobid()
    client = boto3.client("lambda", REGION_NAME)
    response = client.invoke(FunctionName=LR_09_LAMBDA_ARN, LogType="Tail", Payload="{}")

    for key, value in response.items():
        if key == "ResponseMetadata":
            tail_output = base64.b64decode(
                response["ResponseMetadata"]["HTTPHeaders"]["x-amz-log-result"]
            )
            log_output = tail_output.decode("utf-8")
            expected_line = f"Updated JobStatus for jobId='{expected_job_id}'"

            try:
                log_output.index(expected_line)
            except ValueError:
                Messages.write_message("LR-09 scheduled check Unsucessfull")
            else:
                Messages.write_message("LR-09 scheduled check sucessfully completed")

    data = json.loads(response["Payload"].read())
    data_store.scenario["lr_09"] = {"lr_09_data": data}

    actual_job_id = data_store.scenario["lr_09"]["lr_09_data"]["processed_jobs"][0]
    assert expected_job_id == actual_job_id
