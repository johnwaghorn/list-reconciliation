from getgauge.python import step
from getgauge.python import Messages
import shutil
import boto3
import json
import os
from tempfile import gettempdir


# On github
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
region_name = "eu-west-2"

dev = boto3.session.Session(access_key, secret_key)

# Uncomment the below line to run locally and provide the respective profile_name
# dev = boto3.session.Session(profile_name="247275863148_PDS-PoC")

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
filename = "GPR4LNA1.EIA"
test_data = os.path.join(DATA, filename)
bucket = 'test-extract-input-bucket'
temp_dir = gettempdir()


@step("connect and trigger lambda LR-02")
def connect_to_lambda_lr02():
    client = dev.client("lambda", region_name)

    payload_dict = {
  "Records": [
    {
      "eventVersion": "2.0",
      "eventSource": "aws:s3",
      "awsRegion": "eu-west-2",
      "eventTime": "1970-01-01T00:00:00.000Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "EXAMPLE"
      },
      "requestParameters": {
        "sourceIPAddress": "127.0.0.1"
      },
      "responseElements": {
        "x-amz-request-id": "EXAMPLE123456789",
        "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
      },
      "s4": {
        "s3SchemaVersion": "1.0",
        "configurationId": "testConfigRule",
        "bucket": {
          "name": "example-bucket",
          "ownerIdentity": {
            "principalId": "EXAMPLE"
          },
          "arn": "arn:aws:s3:::example-bucket"
        },
        "object": {
          "key": "test/key",
          "size": 1024,
          "eTag": "0123456789abcdef0123456789abcdef",
          "sequencer": "0A1B2C3D4E5F678901"
        }
      }
    }
  ]
}
    lr_02_response = client.invoke(
        FunctionName="arn:aws:lambda:eu-west-2:247275863148:function:LR-02-validate-and-parse",
        InvocationType="Event",
        Payload =json.dumps(payload_dict))

    return lr_02_response


@step("assert response StatusCode in LR-02 lambda response is <StatusCode>")
def assert_lambda_lr_02_response_statuscode(expstatuscode):
    lr_02_response = connect_to_lambda_lr02()

    for key, value in lr_02_response.items():
        print(key, value)
        if key == "StatusCode":
            assert value == int(expstatuscode)


@step("assert responsemetadata HTTPStatusCode in LR-02 response is <StatusCode>")
def assert_lambda_lr_02_response_metadata_statuscode(expstatuscode):
    lr_02_response = connect_to_lambda_lr02()

    for key in lr_02_response.items():
        if key == "ResponseMetadata":
            assert lr_02_response["ResponseMetadata"]["HTTPStatusCode"] == int(
                expstatuscode
            )

@step("connect to s3 and upload file <filename> into inbound folder for LR-02 to pick and validate the file")
def upload_gpextract_file_into_s3(destination_filename):
    s3 = dev.client('s3', region_name)

    try:
        s3.upload_file(test_data, bucket, 'inbound/'+destination_filename)
        print("Upload Successful")
        Messages.write_message("Upload Successful")
        assert True
    except FileNotFoundError:
        print('File not found')
        raise
