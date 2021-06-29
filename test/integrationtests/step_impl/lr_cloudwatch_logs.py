from getgauge.python import step
from datetime import timedelta
from utils.datetimezone import get_datetime_now
from .tf_aws_resources import get_aws_resources

import os

import boto3
import time
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)

aws_resource = get_aws_resources()
LR02_LAMBDA = aws_resource["lr_02_lambda"]['value']

# Region & Timezone
region_name = "eu-west-2"
test_datetime = get_datetime_now()

# aws resources
JOBS_TABLE = aws_resource['jobs_table']['value']
LR02_LAMBDA_LOG_GROUP = f"/aws/lambda/{LR02_LAMBDA}"

client = dev.client("logs", region_name)
request_id = "46753b65-cdb2-4ced-b783-71f7ecd29b7d"
invalid_file_success = "Successfully handled invalid file: GPR4LNA1.EQA"

# Cloud watch Queries
QUERY = f"fields @timestamp, @message | filter @requestId = '{request_id}' | filter @message like /GPR4LNA1.EPA processed successfully/ | sort @timestamp desc | limit 20"
QUERY_LR02_INVALID_PAYLOAD = f"fields @timestamp, @message | sort @timestamp desc | filter @message like /ERROR/ |filter @message like /error_id: 94abeed7-edb6-4dd6-afa0-833bc94a6b25/ |filter @message like /KeyError: 's3'/ | limit 20"
QUERY_LR02_INVALID_DOD = f"fields @timestamp, @message | filter @requestId = '11377ae4-d840-4c8a-82da-00d4a6c95dd2' | filter @message like /{invalid_file_success}/ | sort @timestamp desc | limit 20"


@step(
    "connect to cloudwatch log and assert the response the file is processed successfully"
)
def cloudwatch_file_processed_successfully():
    start_query_response = client.start_query(
        logGroupName=LR02_LAMBDA_LOG_GROUP,
        startTime=int((test_datetime.today() - timedelta(days=365)).timestamp()),
        endTime=int(test_datetime.now().timestamp()),
        queryString=QUERY,
    )
    query_id = start_query_response["queryId"]
    response = None
    while response == None or response["status"] == "Running":
        print("Waiting for query to complete ...")
        time.sleep(10)
        response = client.get_query_results(queryId=query_id)

    for key, value in response.items():
        if key == "results":
            if not value:
                assert False
            else:
                print(*value[0], sep="\n")


@step(
    "connect to cloudwatch log and assert the response for the key error for the key S3 on lambda lr-02"
)
def cloudwatch_for_s3_key_error_on_lambda_lr02_payload():
    start_query_response = client.start_query(
        logGroupName=LR02_LAMBDA_LOG_GROUP,
        startTime=int((test_datetime.today() - timedelta(days=365)).timestamp()),
        endTime=int(test_datetime.now().timestamp()),
        queryString=QUERY_LR02_INVALID_PAYLOAD,
    )
    query_id = start_query_response["queryId"]
    response = None
    while response == None or response["status"] == "Running":
        print("Waiting for query to complete ...")
        time.sleep(10)
        response = client.get_query_results(queryId=query_id)
    for key, value in response.items():
        if key == "results":
            if not value:
                assert False
            else:
                print(*value[0], sep="\n")


@step(
    "connect to cloudwatch log and assert the response for file with invalid date of download"
)
def cloudwatch_for_s3_key_error_on_lambda_lr02_payload():
    start_query_response = client.start_query(
        logGroupName=LR02_LAMBDA_LOG_GROUP,
        startTime=int((test_datetime.today() - timedelta(days=365)).timestamp()),
        endTime=int(test_datetime.now().timestamp()),
        queryString=QUERY_LR02_INVALID_DOD,
    )
    query_id = start_query_response["queryId"]
    response = None
    while response == None or response["status"] == "Running":
        print("Waiting for query to complete ...")
        time.sleep(10)
        response = client.get_query_results(queryId=query_id)
        get_respresult = response.get("results")
        for key in get_respresult[0]:
            print(key)
            for field in key:
                print(field)


@step("get the latest jobid from Jobs table")
def get_latest_jobid():
    dev1 = dev.resource("dynamodb", region_name="eu-west-2")
    job_table = dev1.Table(JOBS_TABLE)
    job_data = job_table.scan()
    job_items = []
    for key, value in job_data.items():
        if key == "Items":
            job_items = [j for j in value]
            job_items = sorted(job_items, reverse=True, key=lambda i: i["Timestamp"])
            latest_job_id = job_items[0]
            return latest_job_id["Id"]


@step("connect to cloudwatch log and get the request id by JobId created")
def connect_to_cloudwatch_get_request_id():
    job_id = get_latest_jobid()
    query_toget_requestid = f"fields @timestamp, @message,@requestId | sort @timestamp desc | filter @message like /Job {job_id} created/ | limit 20"
    start_query_response = client.start_query(
        logGroupName=LR02_LAMBDA_LOG_GROUP,
        startTime=int((test_datetime.today() - timedelta(days=2)).timestamp()),
        endTime=int(test_datetime.now().timestamp()),
        queryString=query_toget_requestid,
    )
    query_id = start_query_response["queryId"]
    response = None

    while response == None or response["status"] == "Running":
        print("Waiting for query to complete ...")
        time.sleep(10)
        response = client.get_query_results(queryId=query_id)
        print(response)
