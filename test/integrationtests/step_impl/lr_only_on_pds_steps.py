from .lr_beforehooks import use_waiters_check_object_exists
from getgauge.python import step
from getgauge.python import Messages
from .test_helpers import PDS_API_ENV
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
DATA = os.path.join(ROOT, "data", PDS_API_ENV)
MOCK_PDS_DATA = get_terraform_output("mock_pds_data")


@step(
    "setup step: upload MESH data <dps_data> on LR-20 and check output in LR-22 for expected file <expected_filename>"
)
def setup_step_connect_to_s3_bucket_lr_20_upload_data(dps_data, expected_filename):
    upload_dps_data = os.path.join(DATA, dps_data)
    s3 = boto3.client("s3", REGION_NAME)
    s3.upload_file(upload_dps_data, LR_20_BUCKET, dps_data)
    use_waiters_check_object_exists(LR_22_BUCKET, f"{expected_filename}")
    lr_22_response = s3.list_objects_v2(Bucket=LR_22_BUCKET)
    Messages.write_message("File upload for the respective GP Practice sucessfully")

    for obj in lr_22_response.get("Contents"):
        s3.get_object(Bucket=LR_22_BUCKET, Key=obj.get("Key"))

    actual_filename = obj.get("Key")
    assert expected_filename == actual_filename
