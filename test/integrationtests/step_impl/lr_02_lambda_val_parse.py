from getgauge.python import step
from getgauge.python import Messages
import boto3
import json
import os
from tempfile import gettempdir
import os
import datetime
import pytz

# On github
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)

# Uncomment the below line to run locally and provide the respective profile_name
# dev = boto3.session.Session(profile_name="247275863148_PDS-PoC")

#Region & Timezone
region_name = "eu-west-2"
datetime = datetime.datetime.now(pytz.timezone('Europe/London'))


ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
bucket = 'test-extract-input-bucket'
temp_dir = gettempdir()


@step("connect and trigger lambda LR-02")
def connect_to_lambda_lr02():
    client = dev.client("lambda", region_name)
    payload_file = 'LR_02_Lambda_Payload.txt'
    payload_temp = os.path.join(DATA, payload_file)
    
    with open(payload_temp) as jsonfile:
        payload_dict = json.load(jsonfile)
    
    lr_02_response = client.invoke(
        FunctionName="arn:aws:lambda:eu-west-2:247275863148:function:LR-02-validate-and-parse",
        InvocationType="Event",
        Payload =json.dumps(payload_dict))

    return lr_02_response


@step("trigger lambda LR-02 and assert response status code is <StatusCode>")
def assert_lambda_lr_02_response_statuscode(expstatuscode):
    lr_02_response = connect_to_lambda_lr02()

    for key, value in lr_02_response.items():
        print(key, value)
        if key == "StatusCode":
            assert value == int(expstatuscode)


@step("trigger lambda LR-02  and assert responsemetadata HTTPStatusCode response is <StatusCode>")
def assert_lambda_lr_02_response_metadata_statuscode(expstatuscode):
    lr_02_response = connect_to_lambda_lr02()

    for key in lr_02_response.items():
        if key == "ResponseMetadata":
            assert lr_02_response["ResponseMetadata"]["HTTPStatusCode"] == int(
                expstatuscode
            )

@step(
    "create the gp_practice file <testfile> for the current date"
)
def create_gp_file_with_current_date(testfile):
    path = os.path.join(DATA, testfile)
    dir_, filename = os.path.split(path)
    filename_no_ext, ext = os.path.splitext(filename)
    now = datetime.datetime.now()
    day = "123456789ABCDEFGHIJKLMNOPQRSTUV"[now.day - 1]
    month = "ABCDEFGHIJKL"[now.month - 1]
    out_path = os.path.join(gettempdir(), f"{filename_no_ext}.{month}{day}A")
    with open(path) as infile, open(out_path, 'w') as outfile:
        outfile.write(infile.read().replace('xxxxxxxx', now.strftime('%Y%m%d')))
    return out_path

@step("connect to s3 and upload file <testfile> into inbound folder for LR-02 to pick and validate the file")
def upload_gpextract_file_into_s3(testfile):
  temp_destdir = create_gp_file_with_current_date(testfile)
  destination_filename = os.path.basename(temp_destdir)
  s3 = dev.client('s3', region_name)
  try:
        s3.upload_file(temp_destdir, bucket, 'inbound/'+destination_filename)
        print("Upload Successful")
        Messages.write_message("Upload Successful")
        assert True
  except FileNotFoundError:
        print('File not found')
        raise

@step("connect and trigger lambda LR-02 with invalid payload")
def connect_to_lambda_lr02_with_invalid_payload():
    client = dev.client("lambda", region_name)
    payload_file = 'LR_02_Lambda_Invalid_Payload.txt'
    payload_temp = os.path.join(DATA, payload_file)
    
    with open(payload_temp) as jsonfile:
        payload_dict = json.load(jsonfile)
    
    lr_02_response = client.invoke(
        FunctionName="arn:aws:lambda:eu-west-2:247275863148:function:LR-02-validate-and-parse",
        InvocationType="Event",
        Payload =json.dumps(payload_dict))

    return lr_02_response