from getgauge.python import Messages, step
from datetime import date, datetime, timedelta


import boto3
import time
import os
import pytz


# On github
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)

# Uncomment the below line to run locally and provide the respective profile_name
#dev = boto3.session.Session(profile_name="247275863148_PDS-PoC")

#Region & Timezone
region_name = "eu-west-2"
datetime = datetime.now(pytz.timezone('Europe/London'))

# log groups
log_group = "/aws/lambda/LR-02-validate-and-parse"

client = dev.client('logs', region_name)
request_id = "46753b65-cdb2-4ced-b783-71f7ecd29b7d"

# Queries
query = f"fields @timestamp, @message | filter @requestId = '{request_id}' | filter @message like /GPR4LNA1.EPA processed successfully/ | sort @timestamp desc | limit 20"
query_requestid = f"fields @timestamp, @message |sort @timestamp desc | limit 20"
query_lr02_invalid_payload =f"fields @timestamp, @message | sort @timestamp desc | filter @message like /ERROR/ |filter @message like /error_id: 94abeed7-edb6-4dd6-afa0-833bc94a6b25/ |filter @message like /KeyError: 's3'/ | limit 20"


@step("connect to cloudwatch log and assert the response the file is processed successfully")
def connect_to_cloudwatch_file_processed_successfully():
    start_query_response = client.start_query(
        logGroupName=log_group,
        startTime=int((datetime.today() - timedelta(days=365)).timestamp()),
        endTime=int(datetime.now().timestamp()),
        queryString=query,
        )
    query_id = start_query_response['queryId']
    response = None
    while response == None or response['status'] == 'Running':
        print('Waiting for query to complete ...')
        time.sleep(10)
        response = client.get_query_results(
            queryId=query_id
                )
    
    for key, value in response.items():
        if (key == "results"):
            if not value:
                assert False
            else : print(*value[0],sep='\n')
            
@step("connect to cloudwatch log and assert the response for the key error for the key S3 on lambda lr-02")
def connect_to_cloudwatch_file_processed_successfully():
    start_query_response = client.start_query(
        logGroupName=log_group,
        startTime=int((datetime.today() - timedelta(days=365)).timestamp()),
        endTime=int(datetime.now().timestamp()),
        queryString=query_lr02_invalid_payload,
        )
    query_id = start_query_response['queryId']
    response = None
    while response == None or response['status'] == 'Running':
            print('Waiting for query to complete ...')
            time.sleep(10)
            response = client.get_query_results(
                queryId=query_id
                )
    for key, value in response.items():
        if (key == "results"):
            if not value:
                assert False
            else : print(*value[0],sep='\n')
@step("connect to cloudwatch log and get the request Id logs")
def connect_to_cloudwatch_get_request_id():
        request_id_query_response = client.start_query(
        logGroupName=log_group,
        startTime=int((datetime.today() - timedelta(minutes=5)).timestamp()),
        endTime=int(datetime.now().timestamp()),
        queryString=query_requestid,
        )
        print(request_id_query_response)
        
        query_id = request_id_query_response['queryId']
        response = None
        while response == None or response['status'] == 'Running':
            print('Waiting for query to complete ...')
            time.sleep(10)
            response = client.get_query_results(
                queryId=query_id
                )
            for key, value in response.items():
                if (key == "results"):
                    if not value:
                        response = client.get_query_results(
                            queryId=query_id)
                    print (key, value)