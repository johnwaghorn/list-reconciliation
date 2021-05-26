from getgauge.python import step
import boto3
import os
import os
import datetime
import pytz


# On github
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)

# Uncomment the below line to run locally and provide the respective profile_name
#dev = boto3.session.Session(profile_name="247275863148_PDS-PoC")

#Region & Timezone
region_name = "eu-west-2"
datetime = datetime.datetime.now(pytz.timezone('Europe/London'))


@step("connect and trigger sqs LR-06 and verify the queue url is correct")
def connect_to_sqs_lr06():
    sqs = dev.client("sqs", region_name)
    queue_url = 'https://eu-west-2.queue.amazonaws.com/247275863148/Patient_Records.fifo'
    lr_06_response = sqs.get_queue_url( QueueName="Patient_Records.fifo")
    actual_queueurl = lr_06_response["QueueUrl"]
    for key, value in lr_06_response.items():
        print( key, value)
    assert actual_queueurl == queue_url
    return lr_06_response

@step("assert response HTTPStatusCode is <expstatuscode> to check sqs LR-06 is active")
def assert_sqs_mss2_response_metadata_statuscode(expstatuscode):
    lr_06_response = connect_to_sqs_lr06()
    for key in lr_06_response.items():
         if key == "ResponseMetadata":
                assert lr_06_response['ResponseMetadata']['HTTPStatusCode'] == int(expstatuscode)