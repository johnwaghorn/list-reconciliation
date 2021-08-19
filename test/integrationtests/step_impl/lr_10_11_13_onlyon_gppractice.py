from .lr_beforehooks import use_waiters_check_object_exists
from getgauge.python import step, Messages, data_store
from utils.datetimezone import get_datetime_now
from .tf_aws_resources import get_terraform_output
from .test_helpers import PDS_API_ENV, get_latest_jobid, await_stepfunction_succeeded

import boto3
import json
import os

REGION_NAME = "eu-west-2"
TEST_DATETIME = get_datetime_now()
LR_10_STATE_FUNCTION_ARN = get_terraform_output("lr_10_sfn_arn")
LR_13_BUCKET = get_terraform_output("lr_13_bucket")
s3 = boto3.client("s3", REGION_NAME)

ROOT = os.path.dirname(os.path.abspath(__file__))
EXPECTED_GP_ONLY_DATA = os.path.join(ROOT, "data", PDS_API_ENV)
stepfunction = boto3.client("stepfunctions", REGION_NAME)


def lr_10_response():
    job_id = get_latest_jobid()
    now = TEST_DATETIME.now()
    time_gen = "%02d%02d%02d%02d%d" % (
        now.year,
        now.month,
        now.day,
        now.minute,
        now.second,
    )
    integ_auto_test = "integ_auto_test_" + time_gen
    lr_10_response = stepfunction.start_execution(
        stateMachineArn=LR_10_STATE_FUNCTION_ARN,
        name=integ_auto_test,
        input=json.dumps({"job_id": job_id}),
    )
    lr_13_fail_response = s3.list_objects_v2(Bucket=LR_13_BUCKET, Prefix=job_id)
    if "Contents" in lr_13_fail_response:
        for object in lr_13_fail_response["Contents"]:
            use_waiters_check_object_exists(LR_13_BUCKET, object["Key"])

    executionarn = lr_10_response["executionArn"]
    return executionarn, job_id


@step("ensure the status of the LR-10 has succeeded for the respective jobid")
def lr_10_exeuction_status():
    job_id = data_store.scenario["lr_09"]["lr_09_data"]["processed_jobs"][0]
    if not job_id:
        job_id = get_latest_jobid()
    response = stepfunction.list_executions(stateMachineArn=LR_10_STATE_FUNCTION_ARN)
    latest_execution = response["executions"][0]["executionArn"]
    sf_output = await_stepfunction_succeeded(latest_execution)

    if sf_output["status"] == "SUCCEEDED":
        # Get the LR-10 output filename and put it into a Gauge datastore so other steps can pick it up
        output = json.loads(sf_output["output"])
        data_store.scenario["lr_10"] = {"job_id": job_id, "output": output}
        if (
            data_store.scenario["lr_10"]["output"]["message"]
            == "Unhandled exception caught in LR14 Lambda"
        ):
            Messages.write_message("Check LR_12, LR_15 and LR_14 lambda Outputs")
            assert False
