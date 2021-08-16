from .lr_beforehooks import use_waiters_check_object_exists

from getgauge.python import step
from getgauge.python import Messages
import boto3
import os
from .tf_aws_resources import get_terraform_output

REGION_NAME = "eu-west-2"

LR_01_BUCKET = get_terraform_output("lr_01_bucket")
LR_01_BUCKET_INBOUND = get_terraform_output("lr_01_bucket_inbound")

LR_12_LAMBDA = get_terraform_output("lr_12_lambda")
LR_20_BUCKET = get_terraform_output("lr_20_bucket")
LR_22_BUCKET = get_terraform_output("lr_22_bucket")
LR_13_BUCKET = get_terraform_output("lr_13_bucket")

EXPECTED_CSV_OUTPUT_FILE = "OnlyOnPDS-Expected-Output.csv"

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
PDS_ONLY_DATA_PATH = "OnlyOnPDS/"
MOCK_PDS_DATA = get_terraform_output("mock_pds_data")


@step(
    "setup step: upload MESH data on LR-20 and check output in LR-22 for expected file <expected_filename>"
)
def setup_step_connect_to_s3_bucket_lr_20_upload_data(expected_filename):
    dps_data = "dps_data.csv"
    upload_dps_data = os.path.join(DATA, PDS_ONLY_DATA_PATH + dps_data)
    s3 = boto3.client("s3", REGION_NAME)

    s3.upload_file(upload_dps_data, LR_20_BUCKET, dps_data)
    use_waiters_check_object_exists(LR_22_BUCKET, f"{expected_filename}")
    lr_22_response = s3.list_objects_v2(Bucket=LR_22_BUCKET)
    Messages.write_message("File upload for the respective GP Practice sucessfully")

    for obj in lr_22_response.get("Contents"):
        s3.get_object(Bucket=LR_22_BUCKET, Key=obj.get("Key"))

    actual_filename = obj.get("Key")
    assert expected_filename == actual_filename


@step(
    "setup step: connect to s3 bucket mock pds api and upload csv file that contains all records from GP flat file"
)
def setup_step_connect_to_mock_data_upload_csv_contains_all_records_from_gp():
    all_pds_api_data = "pds_api_data02.csv"
    upload_pds_mock_data = os.path.join(DATA, PDS_ONLY_DATA_PATH + all_pds_api_data)
    s3 = boto3.client("s3", REGION_NAME)

    try:
        s3.upload_file(upload_pds_mock_data, MOCK_PDS_DATA, all_pds_api_data)
        use_waiters_check_object_exists(MOCK_PDS_DATA, all_pds_api_data)
        Messages.write_message("Mock PDS Data Uploaded Successfully")

    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step("upload a GP flat file that has missing PDS data")
def upload_gp_flat_file_missing_pds_records():
    gp_flat_file = "A76543_GPR4LNA1.GCA"
    upload_gp_flat_file = os.path.join(DATA, PDS_ONLY_DATA_PATH + gp_flat_file)
    s3 = boto3.client("s3", REGION_NAME)

    try:
        s3.upload_file(upload_gp_flat_file, LR_01_BUCKET, "inbound/" + gp_flat_file)
        Messages.write_message("GP Flat File Uploaded Successfully")

    except FileNotFoundError:
        Messages.write_message("File not found")
        raise
