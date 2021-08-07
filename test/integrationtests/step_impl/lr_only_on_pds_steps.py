import os

import boto3
from getgauge.python import Messages, step

from .test_helpers import PDS_API_ENV, await_s3_object_exists
from .tf_aws_resources import get_terraform_output

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", PDS_API_ENV)

LR_20_BUCKET = get_terraform_output("lr_20_bucket")
LR_22_BUCKET = get_terraform_output("lr_22_bucket")


s3 = boto3.client("s3")


@step(
    "setup step: upload PDS supplementary data <dps_data> to LR-20 and check output in LR-22 for expected file <expected_filename>"
)
def setup_step_connect_to_s3_bucket_lr_20_upload_data(dps_data, expected_filename):
    upload_dps_data = os.path.join(DATA, dps_data)
    s3.upload_file(upload_dps_data, LR_20_BUCKET, dps_data.split("/")[1])
    Messages.write_message("File uploaded for the respective GP Practice sucessfully")

    assert await_s3_object_exists(LR_22_BUCKET, expected_filename)
