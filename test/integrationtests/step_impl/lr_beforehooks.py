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
INFLIGHT_TABLE = aws_resource["inflight_table"]["value"]


@step("setup steps: clear all files in LR_01 bucket folders and dynamodb Inflight table")
def before_hooks():
    # Buckets
    response = s3.list_objects_v2(Bucket=LR_01_BUCKET, Prefix="fail/")

    if "Contents" in response:
        for object in response["Contents"]:
            print("Deleting", object["Key"])
            s3.delete_object(Bucket=LR_01_BUCKET, Key=object["Key"])

    lr_13_response = s3.list_objects_v2(Bucket=LR_13_BUCKET)

    if "Contents" in lr_13_response:
        for object in lr_13_response["Contents"]:
            print("Deleting", object["Key"])
            s3.delete_object(Bucket=LR_13_BUCKET, Key=object["Key"])

    # DynamoDB
    dynamodb = dev.resource("dynamodb", region_name="eu-west-2")
    inflight_table = dynamodb.Table(INFLIGHT_TABLE)
    scan = inflight_table.scan()
    with inflight_table.batch_writer() as batch:
        for each in scan["Items"]:
            batch.delete_item(Key={"JobId": each["JobId"]})
