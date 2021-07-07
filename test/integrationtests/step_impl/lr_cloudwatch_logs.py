from getgauge.python import step
from datetime import timedelta
from utils.datetimezone import get_datetime_now
from .tf_aws_resources import get_aws_resources
from .lr_03_dynamodb import get_latest_jobid

import os

import boto3
import time
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# On github
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)

region_name = "eu-west-2"
test_datetime = get_datetime_now()
client = dev.client("logs", region_name)

aws_resource = get_aws_resources()
LR02_LAMBDA = aws_resource["lr_02_lambda"]["value"]

# aws resources
JOBS_TABLE = aws_resource["jobs_table"]["value"]
LR02_LAMBDA_LOG_GROUP = f"/aws/lambda/{LR02_LAMBDA}"


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
