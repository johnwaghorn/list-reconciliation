import os
import sys
from datetime import datetime, timedelta

import boto3
from getgauge.python import step

from .lr_03_dynamodb import get_latest_jobid
from .tf_aws_resources import get_terraform_output

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

region_name = "eu-west-2"
test_datetime = datetime.now()
client = boto3.client("logs", region_name)

LR02_LAMBDA = get_terraform_output("lr_02_lambda")

# aws resources
JOBS_TABLE = get_terraform_output("jobs_table")
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
        response = client.get_query_results(queryId=query_id)
        print(response)
