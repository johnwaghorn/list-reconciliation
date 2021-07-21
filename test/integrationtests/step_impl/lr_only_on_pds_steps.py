import time
from .lr_10_12_13_onlyon_pds import check_output_file_in_lr13
from .lr_03_dynamodb import get_latest_jobid
from getgauge.python import step
from getgauge.python import Messages
import boto3
import os
from tempfile import gettempdir
from .tf_aws_resources import get_aws_resources


# On github
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)


REGION_NAME = "eu-west-2"

AWS_RESOURCE = get_aws_resources()

LR_01_BUCKET = AWS_RESOURCE["lr_01_bucket"]["value"]
LR_01_BUCKET_INBOUND = AWS_RESOURCE["lr_01_bucket_inbound"]["value"]

LR_12_LAMBDA = AWS_RESOURCE["lr_12_lambda"]["value"]
LR_20_BUCKET = AWS_RESOURCE["lr_20_bucket"]["value"]
LR_22_BUCKET = AWS_RESOURCE["lr_22_bucket"]["value"]
LR_13_BUCKET = AWS_RESOURCE["lr_13_bucket"]["value"]

EXPECTED_CSV_OUTPUT_FILE = "OnlyOnPDS-Expected-Output.csv"

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
MOCK_PDS_DATA = AWS_RESOURCE["mock_pds_data"]["value"]


@step("setup step: connect to s3 buckets LR-20 and upload MESH data")
def setup_step_connect_to_s3_bucket_lr_20_upload_data():
    dps_data = "dps_data.csv"
    upload_dps_data = os.path.join(DATA, "OnlyOnPDS/" + dps_data)
    s3 = dev.client("s3", REGION_NAME)

    try:
        s3.upload_file(upload_dps_data, LR_20_BUCKET, dps_data)
        Messages.write_message("DPS file Uploaded Successfully")

    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step(
    "setup step: connect to s3 bucket mock pds api and upload csv file that contains the missing records"
)
def setup_step_connect_to_s3_mock_data_and_upload_csv_missing_records():
    missing_pds_api_data = "pds_api_data.csv"
    upload_pds_mock_data = os.path.join(DATA, "OnlyOnPDS/" + missing_pds_api_data)
    s3 = dev.client("s3", REGION_NAME)

    try:
        s3.upload_file(upload_pds_mock_data, MOCK_PDS_DATA, missing_pds_api_data)
        Messages.write_message("PDS API file Uploaded Successfully")

    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step(
    "setup step: connect to s3 bucket mock pds api and upload csv file that contains all records from GP flat file"
)
def setup_step_connect_to_mock_data_upload_csv_contains_all_records_from_gp():
    all_pds_api_data = "pds_api_data02.csv"
    upload_pds_mock_data = os.path.join(DATA, "OnlyOnPDS/" + all_pds_api_data)
    s3 = dev.client("s3", REGION_NAME)

    try:
        s3.upload_file(upload_pds_mock_data, MOCK_PDS_DATA, all_pds_api_data)
        Messages.write_message("Mock PDS Data Uploaded Successfully")

    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step("upload a GP flat file that has missing PDS data")
def upload_gp_flat_file_missing_pds_records():
    gp_flat_file = "A76543_GPR4LNA1.GCA"
    upload_gp_flat_file = os.path.join(DATA, "OnlyOnPDS/" + gp_flat_file)
    s3 = dev.client("s3", REGION_NAME)

    try:
        s3.upload_file(upload_gp_flat_file, LR_01_BUCKET, "inbound/" + gp_flat_file)
        Messages.write_message("GP Flat File Uploaded Successfully")

    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step("check LR-13 does not contain OnlyOnPDS data")
def check_lr_13_job_folder_does_not_contain_pds_csv():
    time.sleep(10)
    job_id_prefix = get_latest_jobid()
    s3_client = dev.client("s3", REGION_NAME)
    response = s3_client.list_objects_v2(Bucket=LR_13_BUCKET, Prefix=job_id_prefix)

    file_count = response["KeyCount"]

    assert file_count == 2


@step("connect to lr-13 and check for latest output csv file for OnlyOnPDS")
def check_lr_13_has_output_csv_file_for_only_on_pds():
    job_id_prefix = get_latest_jobid()
    check_output_file_in_lr13(job_id_prefix, "A76543")


@step("delete all s3 files in LR22")
def delete_s3_file_from_lr_22():
    s3_client = dev.client("s3", REGION_NAME)
    lr_22_response = s3_client.list_objects_v2(Bucket=LR_22_BUCKET)

    for object in lr_22_response["Contents"]:
        print("Deleting", object["Key"])
        s3_client.delete_object(Bucket=LR_22_BUCKET, Key=object["Key"])

    Messages.write_message("Deleted all s3 files in lr-22 bucket")


@step("delete all csv files in LR13")
def delete_all_s3_files_in_lr13():
    s3_client = dev.client("s3", REGION_NAME)
    lr_13_response = s3_client.list_objects_v2(Bucket=LR_13_BUCKET)

    for object in lr_13_response["Contents"]:
        print("Deleting", object["Key"])
        s3_client.delete_object(Bucket=LR_13_BUCKET, Key=object["Key"])

    Messages.write_message("Deleted all s3 files in lr-13 bucket")
