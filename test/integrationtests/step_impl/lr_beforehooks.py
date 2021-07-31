import boto3
from getgauge.python import Messages, step

from .tf_aws_resources import get_terraform_output


LR_01_BUCKET = get_terraform_output("lr_01_bucket")
LR_13_BUCKET = get_terraform_output("lr_13_bucket")
LR_22_BUCKET = get_terraform_output("lr_22_bucket")
LR_23_BUCKET = get_terraform_output("lr_23_bucket")
MOCK_PDS_DATA = get_terraform_output("mock_pds_data")
INFLIGHT_TABLE = get_terraform_output("in_flight_table")

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")


def use_waiters_check_object_exists(bucket_name, key_name):
    try:
        waiter = s3.get_waiter("object_exists")
        waiter.wait(Bucket=bucket_name, Key=key_name, WaiterConfig={"Delay": 10, "MaxAttempts": 5})
        Messages.write_message("Object exists: " + bucket_name + "/" + key_name)

    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step("setup steps: clear all files in LR_01 bucket folders and dynamodb Inflight table")
def before_hooks_lr01_inflight_db():
    # Bucket lr01_Fail Folder
    lr_01_fail_response = s3.list_objects_v2(Bucket=LR_01_BUCKET, Prefix="fail/")
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

    # Bucket lr13 Folder
    lr_13_response = s3.list_objects_v2(Bucket=LR_13_BUCKET)

    if "Contents" in lr_13_response:
        for object in lr_13_response["Contents"]:
            Messages.write_message(f"Deleting {LR_13_BUCKET}/{object['Key']}")
            s3.delete_object(Bucket=LR_13_BUCKET, Key=object["Key"])

    # DynamoDB - Inflight table
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
            Messages.write_message(f"Deleting {MOCK_PDS_DATA}/{object['Key']}")
            s3.delete_object(Bucket=MOCK_PDS_DATA, Key=object["Key"])

    # Bucket lr22_bucket
    lr_22_response = s3.list_objects_v2(Bucket=LR_22_BUCKET)
    if "Contents" in lr_22_response:
        for object in lr_22_response["Contents"]:
            Messages.write_message(f"Deleting {LR_22_BUCKET}/{object['Key']}")
            s3.delete_object(Bucket=LR_22_BUCKET, Key=object["Key"])


@step("setup steps: clear all files lr_23 bucket")
def before_hooks_lr23_bucket_data():
    # Bucket lr22_bucket
    lr_23_response = s3.list_objects_v2(Bucket=LR_23_BUCKET)
    if "Contents" in lr_23_response:
        for object in lr_23_response["Contents"]:
            Messages.write_message(f"Deleting {LR_23_BUCKET}/{object['Key']}")
            s3.delete_object(Bucket=LR_23_BUCKET, Key=object["Key"])


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
    tableKeyNames = [key.get("AttributeName") for key in table.key_schema]

    # Only retrieve the keys for each item in the table (minimize data transfer)
    projectionExpression = ", ".join("#" + key for key in tableKeyNames)
    expressionAttrNames = {"#" + key: key for key in tableKeyNames}

    counter = 0
    page = table.scan(
        ProjectionExpression=projectionExpression, ExpressionAttributeNames=expressionAttrNames
    )
    with table.batch_writer() as batch:
        while page["Count"] > 0:
            counter += page["Count"]
            # Delete items in batches
            for itemKeys in page["Items"]:
                batch.delete_item(Key=itemKeys)
            # Fetch the next page
            if "LastEvaluatedKey" in page:
                page = table.scan(
                    ProjectionExpression=projectionExpression,
                    ExpressionAttributeNames=expressionAttrNames,
                    ExclusiveStartKey=page["LastEvaluatedKey"],
                )
            else:
                break
