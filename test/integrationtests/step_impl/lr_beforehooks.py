import boto3
import time
from getgauge.python import Messages, step
from .tf_aws_resources import get_terraform_output

LR_01_BUCKET = get_terraform_output("lr_01_bucket")
LR_13_BUCKET = get_terraform_output("lr_13_bucket")
LR_22_BUCKET = get_terraform_output("lr_22_bucket")
INFLIGHT_TABLE = get_terraform_output("in_flight_table")

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")


def use_waiters_check_object_exists(bucket_name, key_name):
    try:
        waiter = s3.get_waiter("object_exists")
        waiter.wait(Bucket=bucket_name, Key=key_name, WaiterConfig={"Delay": 10, "MaxAttempts": 8})
        Messages.write_message("Object exists: " + bucket_name + "/" + key_name)

    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step("setup steps: clear all files in LR_01 bucket folders")
def before_hooks_lr01():
    # Bucket lr01_Fail Folder
    lr_01_fail_response = s3.list_objects_v2(Bucket=LR_01_BUCKET, Prefix="fail")
    if "Contents" in lr_01_fail_response:
        for object in lr_01_fail_response["Contents"]:
            Messages.write_message(f"Deleting {LR_01_BUCKET}/{object['Key']}")
            s3.delete_object(Bucket=LR_01_BUCKET, Key=object["Key"])

    # Bucket lr01_Pass Folder
    lr_01_pass_response = s3.list_objects_v2(Bucket=LR_01_BUCKET, Prefix="pass/")
    if "Contents" in lr_01_pass_response:
        for object in lr_01_pass_response["Contents"]:
            Messages.write_message(f"Deleting {LR_01_BUCKET}/{object['Key']}")
            s3.delete_object(Bucket=LR_01_BUCKET, Key=object["Key"])


@step("setup: empty bucket <bucket>")
def before_hooks_empty_bucket(bucket):
    bucket_name = get_terraform_output(bucket)
    Messages.write_message(f"Emptying bucket: {bucket_name}")
    response = s3.list_objects_v2(Bucket=bucket_name)
    for object in response.get("Contents", []):
        Messages.write_message(f"Deleting: s3://{bucket_name}/{object['Key']}")
        s3.delete_object(Bucket=bucket_name, Key=object["Key"])


@step("setup: empty table <table>")
def before_hooks_empty_table(table):
    table = dynamodb.Table(get_terraform_output(table))

    # get the table keys
    tablekeynames = [key.get("AttributeName") for key in table.key_schema]

    # Only retrieve the keys for each item in the table (minimize data transfer)
    projectionexpression = ", ".join("#" + key for key in tablekeynames)
    expressionattrnames = {"#" + key: key for key in tablekeynames}

    counter = 0
    page = table.scan(
        ProjectionExpression=projectionexpression, ExpressionAttributeNames=expressionattrnames
    )
    with table.batch_writer() as batch:
        while page["Count"] > 0:
            counter += page["Count"]
            # Delete items in batches
            for itemkeys in page["Items"]:
                batch.delete_item(Key=itemkeys)
            # Fetch the next page
            if "LastEvaluatedKey" in page:
                page = table.scan(
                    ProjectionExpression=projectionexpression,
                    ExpressionAttributeNames=expressionattrnames,
                    ExclusiveStartKey=page["LastEvaluatedKey"],
                )
            else:
                break


@step("wait for <seconds> seconds to allow other jobs to process")
def wait_for_seconds(seconds):
    time.sleep(int(seconds))
