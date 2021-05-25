from getgauge.python import Messages, step
from datetime import date, datetime, timedelta


import boto3
import time
import os
import pytz


# On github
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")#
dev = boto3.session.Session(access_key, secret_key)

#Region & Timezone
region_name = "eu-west-2"
datetime = datetime.now(pytz.timezone('Europe/London'))


# Uncomment the below line to run locally and provide the respective profile_name
# dev = boto3.session.Session(profile_name="247275863148_PDS-PoC")

client = dev.client('logs', region_name)
log_group = "/aws/lambda/LR-02-validate-and-parse"
request_id = "27e3e0cb-aba2-42d9-85bd-8beada107df0"

# Queries
query = "fields @timestamp, @message | filter @message like /GPR4LNA1.EIA processed successfully/ | sort @timestamp desc | limit 1" 
query_requestid = f'("fields @timestamp, @message |filter @requestId ={request_id} |sort @timestamp desc | limit 20")'



@step("connect to cloudwatch log and assert the response the file is processed successfully")
def connect_to_cloudwatch_file_processed_successfully():
    start_query_response = client.start_query(
        logGroupName=log_group,
        startTime=int((datetime.today() - timedelta(minutes=5)).timestamp()),
        endTime=int(datetime.now().timestamp()),
        queryString=query,
        )
    query_id = start_query_response['queryId']
    response = None
    while response == None or response['status'] == 'Running':
            print('Waiting for query to complete ...')
            time.sleep(1)
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