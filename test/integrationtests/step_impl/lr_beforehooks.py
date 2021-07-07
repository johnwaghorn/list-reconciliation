from getgauge.python import step
from .tf_aws_resources import get_aws_resources

import boto3
import os


access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)

aws_resource = get_aws_resources()
s3 = dev.client("s3")
LR_01_BUCKET = aws_resource["lr_01_bucket"]["value"]


@step("setup steps: clear all files in lr01 folders")
def before_hooks():
    response = s3.list_objects_v2(Bucket=LR_01_BUCKET, Prefix="fail/")

    if "Contents" in response:
        for object in response["Contents"]:
            print("Deleting", object["Key"])
            s3.delete_object(Bucket=LR_01_BUCKET, Key=object["Key"])
