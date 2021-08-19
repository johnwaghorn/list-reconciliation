from .test_helpers import PDS_API_ENV
from .lr_beforehooks import use_waiters_check_object_exists
from getgauge.python import step
from getgauge.python import Messages
import boto3
import os
from .tf_aws_resources import get_terraform_output

REGION_NAME = "eu-west-2"
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(PDS_API_ENV, "LR_22")
LR_22_BUCKET = get_terraform_output("lr_22_bucket")


@step("connect to s3 lr-22 bucket and upload pds data")
def connect_to_s3_and_upload_pds_data(pds_data):
    upload_pds_data = os.path.join(DATA, pds_data)
    s3 = boto3.client("s3", REGION_NAME)
    try:
        s3.upload_file(upload_pds_data, LR_22_BUCKET, pds_data)
        use_waiters_check_object_exists(LR_22_BUCKET, pds_data)
        Messages.write_message("PDS data Upload on LR-22 is Successful")

    except FileNotFoundError:
        Messages.write_message("File not found")
        raise
