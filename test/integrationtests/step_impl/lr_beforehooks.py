from getgauge.python import step
from .tf_aws_resources import get_aws_resources

import boto3
import os

# On github
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)

aws_resource = get_aws_resources()
s3 = dev.client("s3")
LR_01_BUCKET = aws_resource["lr_01_bucket"]["value"]
LR_13_BUCKET = aws_resource["lr_13_bucket"]["value"]
LR_22_BUCKET = aws_resource["lr_22_bucket"]["value"]
LR_23_BUCKET = aws_resource["lr_23_bucket"]["value"]
MOCK_PDS_DATA = aws_resource["mock_pds_data"]["value"]
INFLIGHT_TABLE = aws_resource["in_flight_table"]["value"]


@step("setup steps: clear all files in LR_01 bucket folders and dynamodb Inflight table")
def before_hooks_lr01_inflight_db():
    # Bucket lr01_Fail Folder
    lr_01_fail_response = s3.list_objects_v2(Bucket=LR_01_BUCKET, Prefix="fail/")
    if "Contents" in lr_01_fail_response:
        for object in lr_01_fail_response["Contents"]:
            print("Deleting", object["Key"])
            s3.delete_object(Bucket=LR_01_BUCKET, Key=object["Key"])

    # Bucket lr01_Pass Folder
    lr_01_pass_response = s3.list_objects_v2(Bucket=LR_01_BUCKET, Prefix="pass/")

    if "Contents" in lr_01_pass_response:
        for object in lr_01_pass_response["Contents"]:
            print("Deleting", object["Key"])
            s3.delete_object(Bucket=LR_01_BUCKET, Key=object["Key"])

    # Bucket lr13 Folder
    lr_13_response = s3.list_objects_v2(Bucket=LR_13_BUCKET)

    if "Contents" in lr_13_response:
        for object in lr_13_response["Contents"]:
            print("Deleting", object["Key"])
            s3.delete_object(Bucket=LR_13_BUCKET, Key=object["Key"])

    # DynamoDB - Inflight table
    dynamodb = dev.resource("dynamodb", region_name="eu-west-2")
    inflight_table = dynamodb.Table(INFLIGHT_TABLE)
    scan = inflight_table.scan()
    with inflight_table.batch_writer() as batch:
        for each in scan["Items"]:
            batch.delete_item(Key={"JobId": each["JobId"]})


@step("setup steps: clear all files in mock pds data and lr_22 buckets")
def before_hooks_pds_data():
    # Bucket mock_pds_data
    mock_pds_data_response = s3.list_objects_v2(Bucket=MOCK_PDS_DATA)
    if "Contents" in mock_pds_data_response:
        for object in mock_pds_data_response["Contents"]:
            print("Deleting", object["Key"])
            s3.delete_object(Bucket=MOCK_PDS_DATA, Key=object["Key"])

    # Bucket lr22_bucket
    lr_22_response = s3.list_objects_v2(Bucket=LR_22_BUCKET)
    if "Contents" in lr_22_response:
        for object in lr_22_response["Contents"]:
            print("Deleting", object["Key"])
            s3.delete_object(Bucket=LR_22_BUCKET, Key=object["Key"])


@step("setup steps: clear all files lr_23 bucket")
def before_hooks_lr23_bucket_data():
    # Bucket lr22_bucket
    lr_23_response = s3.list_objects_v2(Bucket=LR_23_BUCKET)
    if "Contents" in lr_23_response:
        for object in lr_23_response["Contents"]:
            print("Deleting", object["Key"])
            s3.delete_object(Bucket=LR_23_BUCKET, Key=object["Key"])
