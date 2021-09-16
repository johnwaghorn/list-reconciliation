import json
import os

import boto3
from getgauge.python import Messages, data_store, step
from jobs.statuses import InputFolderType

from .lr_02_lambda_val_parse import create_gp_file
from .lr_beforehooks import use_waiters_check_object_exists
from .test_helpers import (
    PDS_API_ENV,
    await_s3_object_exists,
    await_stepfunction_succeeded,
    create_timestamp,
    get_latest_jobid,
)
from .tf_aws_resources import get_terraform_output

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", PDS_API_ENV)

LR_01_BUCKET = get_terraform_output("lr_01_bucket")
LR_10_STATE_FUNCTION_ARN = get_terraform_output("lr_10_sfn_arn")
LR_13_BUCKET = get_terraform_output("lr_13_bucket")
LR_22_BUCKET = get_terraform_output("lr_22_bucket")

REGION_NAME = "eu-west-2"
dynamodb = boto3.resource("dynamodb", REGION_NAME)
s3 = boto3.client("s3", REGION_NAME)
stepfunctions = boto3.client("stepfunctions", REGION_NAME)


@step("upload test data files in <path> to lr-22")
def upload_test_data_files_to_lr_22(path):
    try:
        for file in ["Y12345.csv", "Y123451.csv", "Y123452.csv"]:
            s3.upload_file(os.path.join(DATA, path, file), LR_22_BUCKET, file)
            use_waiters_check_object_exists(LR_22_BUCKET, file)
        Messages.write_message("Test data uploaded")
    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step("upload test data file <filename> in <path> to lr-22")
def upload_test_data_files_in_path_to_lr_22(filename, path):
    try:
        s3.upload_file(os.path.join(DATA, path, filename), LR_22_BUCKET, filename)
        use_waiters_check_object_exists(LR_22_BUCKET, filename)
        Messages.write_message("Test data uploaded")
    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step("upload gpfile file <testfile> to LR-01")
def upload_gpextract_file_into_s3(testfile):
    gp_file = create_gp_file(testfile, "DOW~1")
    destination_filename = os.path.basename(gp_file)
    try:
        s3.upload_file(
            gp_file, LR_01_BUCKET, f"{InputFolderType.IN.value}{destination_filename}"
        )
        use_waiters_check_object_exists(
            LR_01_BUCKET, f"{InputFolderType.PASS.value}{destination_filename}"
        )
        Messages.write_message("Upload Successful")
    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step("execute step function lr-10 and assert status succeeded")
def execute_step_function_lr_10_assert_succeeded():
    # Get the latest Job ID and put it into a Gauge datastore so other steps can pick it up
    job_id = get_latest_jobid()
    Messages.write_message(f"JOB_ID {job_id}")
    data_store.scenario["job_id"] = job_id

    execution = stepfunctions.start_execution(
        stateMachineArn=LR_10_STATE_FUNCTION_ARN,
        name=f"integration_test_{create_timestamp()}",
        input=json.dumps({"job_id": job_id}),
    )

    stepfunction = await_stepfunction_succeeded(execution["executionArn"])

    if stepfunction["status"] == "SUCCEEDED":
        # Get the LR-10 output filename and put it into a Gauge datastore so other steps can pick it up
        output = json.loads(stepfunction["output"])
        data_store.scenario["lr_10"] = {"job_id": job_id, "output": output}
        if (
            data_store.scenario["lr_10"]["output"]["message"]
            == "Unhandled exception caught in LR14 Lambda"
        ):
            Messages.write_message("Check LR_12, LR_15 and LR_14 lambda Outputs")
            assert False
        assert True


@step(
    "ensure produced <filetype> file contains the expected consolidated records as in <expected_data_file>"
)
def assert_expected_file_in_lr13(filetype, expected_data_file):
    job_id = data_store.scenario["lr_10"]["job_id"]

    if not job_id:
        job_id = get_latest_jobid()

    lr_10 = data_store.scenario["lr_10"]
    if not lr_10:
        assert False
    try:
        expected_filename = next(
            file for file in lr_10["output"]["files"] if filetype in file
        )
        bucket = LR_13_BUCKET
        key = f"{job_id}/{expected_filename}"

    except StopIteration:
        assert False, f"{filetype} is wrong"

    assert await_s3_object_exists(
        bucket, key
    ), f"Could not find file: {bucket}/{key} for job_id: {job_id}"
    assert filetype in key, f"Output file: {bucket}/{key} was not type: {filetype}"

    job_object = s3.get_object(Bucket=LR_13_BUCKET, Key=key)
    sorted_job_data = sorted(job_object["Body"].read().decode("utf-8").splitlines())

    expected_data_path = os.path.join(DATA, expected_data_file)
    with open(expected_data_path) as expected_data:
        sorted_expected_data = sorted(expected_data)
        for job_row, expected_row in zip(sorted_job_data, sorted_expected_data):
            assert (
                job_row.rstrip() == expected_row.rstrip()
            ), f"File: {bucket}/{key}\nJob row: {job_row}\nExpected row: {expected_row}\nError: expected record not found"
