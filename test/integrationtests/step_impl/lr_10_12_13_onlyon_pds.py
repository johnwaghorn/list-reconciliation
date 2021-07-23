import time
from getgauge.python import step
from getgauge.python import Messages
import boto3
import os
import json
import uuid
from tempfile import gettempdir
from .tf_aws_resources import get_terraform_output
from utils.datetimezone import get_datetime_now


# On github
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)
REGION_NAME = "eu-west-2"

test_datetime = get_datetime_now()

LR_12_LAMBDA = get_terraform_output("lr_12_lambda")
LR_10_STATE_FUNCTION_ARN = get_terraform_output("lr_10_sfn_arn")
LR_10_JOB_ID = '{"job_id" : "41f678df-9210-45df-8f1e-330ee96acdc8"}'
LR_22_BUCKET = get_terraform_output("lr_22_bucket")
LR_13_BUCKET = get_terraform_output("lr_13_bucket")
DYNAMODB_DEMOG = get_terraform_output("demographic_table")
DYNAMODB_INFLIGHTS = get_terraform_output("in_flight_table")
DYNAMODB_JOBS = get_terraform_output("jobs_table")
DYNAMODB_JOBSTATS = get_terraform_output("jobs_stats_table")

LR_12_LAMBDA_PAYLOAD = "LR_12_Lambda_Payload.txt"
EXECUTION_NAME = "automate-lr-10-stepfunction"
EXAMPLE_OUTPUT = "test"
PREFIX_S3 = "41f678df-9210-45df-8f1e-330ee96acdc8"

EXPECTED_CSV_OUTPUT_FILE = "OnlyOnPDS-Expected-Output.csv"

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
MOCK_PDS_DATA = get_terraform_output("mock_pds_data")

temp_dir = gettempdir()


@step("delete all s3 files in LR13")
def delete_all_s3_files_in_lr13():
    s3_client = dev.client("s3", REGION_NAME)
    lr_13_response = s3_client.list_objects_v2(Bucket=LR_13_BUCKET, Prefix=PREFIX_S3)
    if "Contents" in lr_13_response:
        for object in lr_13_response["Contents"]:
            print("Deleting", object["Key"])
            s3_client.delete_object(Bucket=LR_13_BUCKET, Key=object["Key"])

    Messages.write_message("Deleted all s3 files in lr-13 bucket")


@step("connect to dynamodb and add records")
def connect_to_db_and_add_data():
    payload_01 = os.path.join(DATA, "LR_12/record01.json")
    payload_02 = os.path.join(DATA, "LR_12/record02.json")

    with open(payload_01) as jsonfile:
        record_item_01 = json.load(jsonfile)
    with open(payload_02) as jsonfile:
        record_item_02 = json.load(jsonfile)

    add_to_dynamodb = dev.resource("dynamodb", REGION_NAME)

    demographics = add_to_dynamodb.Table(DYNAMODB_DEMOG)
    demographics.put_item(Item=record_item_01)
    demographics.put_item(Item=record_item_02)

    jobs_table = add_to_dynamodb.Table(DYNAMODB_JOBS)
    jobs_table.put_item(
        Item={
            "FileName": "Y123452_GPR4LNA1.F6A",
            "Id": "41f678df-9210-45df-8f1e-330ee96acdc8",
            "PracticeCode": "Y123452",
            "StatusId": "1",
            "Timestamp": "2021-06-17T15:53:47.301982+0000",
        }
    )

    job_stats_table = add_to_dynamodb.Table(DYNAMODB_JOBSTATS)
    job_stats_table.put_item(
        Item={
            "JobId": "41f678df-9210-45df-8f1e-330ee96acdc8",
            "OnlyOnGpRecords": 0,
            "OnlyOnPdsRecords": 2,
        }
    )

    Messages.write_message("DynamoDB data uploaded")


@step("connect to s3 bucket LR-22 and mock pds and upload data files")
def connect_to_s3_and_upload_mock_data():
    pds_api_data_file = "pds_api_data.csv"
    pds_data_set01 = "Y123451.csv"
    pds_data_set02 = "Y123452.csv"

    upload_pds_data = os.path.join(DATA, "LR_12/" + pds_api_data_file)
    upload_pds_data_set1 = os.path.join(DATA, "LR_12/" + pds_data_set01)
    upload_pds_data_set02 = os.path.join(DATA, "LR_12/" + pds_data_set02)

    s3 = dev.client("s3", REGION_NAME)

    try:
        s3.upload_file(upload_pds_data, MOCK_PDS_DATA, pds_api_data_file)
        s3.upload_file(upload_pds_data_set1, LR_22_BUCKET, pds_data_set01)
        s3.upload_file(upload_pds_data_set02, LR_22_BUCKET, pds_data_set02)
        Messages.write_message("All PDS files Upload Successful")

    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step("connect to step function LR-10 and pass in job id and return successful execution response")
def connect_to_step_function_successfully():
    step_function_client = dev.client("stepfunctions", REGION_NAME)
    lr_10_response = step_function_client.start_execution(
        stateMachineArn=LR_10_STATE_FUNCTION_ARN,
        name=str(uuid.uuid4()),
        input=LR_10_JOB_ID,
    )
    time.sleep(5)
    execution_arn = lr_10_response["executionArn"]
    desc_exec_resp = step_function_client.describe_execution(executionArn=execution_arn)
    status = desc_exec_resp["status"]

    while status != "SUCCEEDED":
        if status == "FAILED":
            Messages.write_message("LR 10 StepFunction failed")
            Messages.write_message(status)
            Messages.write_message(desc_exec_resp)
            Messages.write_message(execution_arn)
            assert False
        else:
            desc_exec_resp = step_function_client.describe_execution(executionArn=execution_arn)
            status = desc_exec_resp["status"]

    Messages.write_message("Executed LR-10 Successfully")


@step("check lambda LR-12 has run")
def check_lambda_lr12_has_processed_record():
    client = dev.client("lambda", REGION_NAME)
    payload_file = LR_12_LAMBDA_PAYLOAD
    payload_temp = os.path.join(DATA, "LR_12/" + payload_file)

    with open(payload_temp) as jsonfile:
        payload_dict = json.load(jsonfile)

    lr_12_response = client.invoke(
        FunctionName=LR_12_LAMBDA,
        InvocationType="Event",
        Payload=json.dumps(payload_dict),
    )

    for key, value in lr_12_response.items():
        if key == "ResponseMetadata":
            assert lr_12_response["ResponseMetadata"]["HTTPStatusCode"] == (202)

    Messages.write_message("lr-12 executed successfully")


@step(
    "connect to lr-13 and check output csv file content and file format as expected for <Job Id> and <GP ODS Code>"
)
def check_output_file_in_lr13(job_id, gp_ods_code):
    time.sleep(10)
    s3_client = dev.client("s3", REGION_NAME)
    response = s3_client.list_objects_v2(Bucket=LR_13_BUCKET, Prefix=job_id)

    for obj in response.get("Contents"):
        print("Found CSV File", obj["Key"])
        s3_client.get_object(Bucket=LR_13_BUCKET, Key=obj.get("Key"))

    expected_string = obj.get("Key")
    filename, ext = os.path.splitext(expected_string)
    elements = "-".join(filename.split("-")[0:6])
    assert elements == f"{job_id}/{gp_ods_code}-OnlyOnPDS"
    assert ext == ".csv"
