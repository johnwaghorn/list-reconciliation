import time

import boto3
import botocore

from .aws import get_terraform_output


dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
stepfunctions = boto3.client("stepfunctions")
PDS_URL = get_terraform_output("pds_url")
PDS_API_ENV = PDS_URL.split("/")[2].split(".")[0]


def await_s3_object_exists(bucket, key):
    try:
        waiter = s3.get_waiter("object_exists")
        waiter.wait(Bucket=bucket, Key=key)
        print(f"Object exists: {bucket}/{key}")
        return True
    except botocore.exceptions.WaiterError:
        print(f"Object not found after waiting: {bucket}/{key}")
        return False


def await_stepfunction_succeeded(execution_arn, poll_limit=6, poll_count=0, poll_sleep=10):
    while True:
        describe_execution = stepfunctions.describe_execution(executionArn=execution_arn)
        status = describe_execution["status"]
        output = describe_execution.get("output")

        if status == "SUCCEEDED" and output:
            return describe_execution
        else:
            poll_count += 1

        if poll_count >= poll_limit:
            print(f"LR 10 StepFunction arn: {execution_arn} status: {status}")
            return describe_execution

        time.sleep(poll_sleep)


def empty_s3_bucket(bucket):
    bucket_name = get_terraform_output(bucket)
    response = s3.list_objects_v2(Bucket=bucket_name)
    for object in response.get("Contents", []):
        s3.delete_object(Bucket=bucket_name, Key=object["Key"])


def empty_dynamodb_table(table):
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
