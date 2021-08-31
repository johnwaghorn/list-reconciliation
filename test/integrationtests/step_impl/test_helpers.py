import time
from datetime import datetime

import boto3
import botocore
from getgauge.python import Messages

from .tf_aws_resources import get_terraform_output

REGION_NAME = "eu-west-2"
dynamodb = boto3.resource("dynamodb", REGION_NAME)
s3 = boto3.client("s3", REGION_NAME)
stepfunctions = boto3.client("stepfunctions", REGION_NAME)
PDS_URL = get_terraform_output("pds_url")
PDS_API_ENV = PDS_URL.split("/")[2].split(".")[0]


def await_s3_object_exists(bucket, key):
    try:
        waiter = s3.get_waiter("object_exists")
        waiter.wait(Bucket=bucket, Key=key)
        Messages.write_message(f"Object exists: {bucket}/{key}")
        return True
    except botocore.exceptions.WaiterError:
        Messages.write_message(f"Object not found after waiting: {bucket}/{key}")
        return False


def get_latest_jobid():
    job_table = dynamodb.Table(get_terraform_output("jobs_table"))
    job_items = [j for j in job_table.scan()["Items"]]
    job_items = sorted(job_items, reverse=True, key=lambda i: i["Timestamp"])
    return job_items[0]["Id"]


def create_timestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S%f")


def await_stepfunction_succeeded(execution_arn, poll_limit=6, poll_count=0, poll_sleep=10):
    while True:
        describe_execution = stepfunctions.describe_execution(executionArn=execution_arn)
        status = describe_execution["status"]
        output = describe_execution.get("output")

        if status == "SUCCEEDED" and output:
            return describe_execution
        else:
            poll_count += 1

        if poll_count >= poll_limit:
            Messages.write_message(f"LR 10 StepFunction arn: {execution_arn} status: {status}")
            return describe_execution

        time.sleep(poll_sleep)


def is_content_present(response):
    return "Contents" in response
