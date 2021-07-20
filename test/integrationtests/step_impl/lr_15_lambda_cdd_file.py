from getgauge.python import step
from getgauge.python import Messages
from tempfile import gettempdir
from .tf_aws_resources import get_terraform_output
from utils.datetimezone import get_datetime_now

import boto3
import os
import time

# On github
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)

test_datetime = get_datetime_now()
temp_dir = gettempdir()

REGION_NAME = "eu-west-2"
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
EXPECED_DATA = os.path.join(ROOT, "data")

MOCK_PDS_DATA = get_terraform_output("mock_pds_data")
LR_12_LAMBDA = get_terraform_output("lr_12_lambda")
LR_10_STATE_FUNCTION_ARN = get_terraform_output("lr_10_sfn_arn")
LR_22_BUCKET = get_terraform_output("lr_22_bucket")
LR_13_BUCKET = get_terraform_output("lr_13_bucket")
LR_23_BUCKET = get_terraform_output("lr_23_bucket")
DYNAMODB_DEMOG = get_terraform_output("demographic_table")
DYNAMODB_INFLIGHTS = get_terraform_output("in_flight_table")
DYNAMODB_JOBS = get_terraform_output("jobs_table")
DYNAMODB_JOBSTATS = get_terraform_output("jobs_stats_table")


@step("prep step : connect to s3 buckets mock pds, lr-22 and upload data files for <lr-15> lambda")
def connect_to_s3_and_upload_mock_data_valid_scenario(lr_15_path):
    s3 = dev.client("s3", REGION_NAME)

    try:
        s3.upload_file(
            os.path.join(DATA, lr_15_path + "pds_api_data.csv"),
            MOCK_PDS_DATA,
            "pds_api_data.csv",
        )
        s3.upload_file(os.path.join(DATA, "LR_15/A82023.csv"), LR_22_BUCKET, "A82023.csv")
        s3.upload_file(os.path.join(DATA, "LR_15/Y123451.csv"), LR_22_BUCKET, "Y123451.csv")
        s3.upload_file(os.path.join(DATA, "LR_15/Y123452.csv"), LR_22_BUCKET, "Y123452.csv")
        time.sleep(5)
        Messages.write_message("All PDS data related files Uploaded Successful")

    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step(
    "connect to <lr_bucket> s3 bucket and ensure <filetype> produced contains the expected consolidated records as in <exp_datafile>"
)
def assert_expected_file_in_lr13(lr_bucket, filetype, exp_datafile):
    exp_path = os.path.join(EXPECED_DATA, lr_bucket + exp_datafile)

    s3 = dev.client("s3", REGION_NAME)
    result = s3.list_objects(Bucket=LR_13_BUCKET)
    with open(exp_path, "r") as exp_datafile:
        exp_data = sorted(exp_datafile)

        for filename in result.get("Contents"):
            if filetype in filename:
                data = s3.get_object(Bucket=LR_13_BUCKET, Key=filename.get("Key"))
                act_contents = sorted(data["Body"].read().decode("utf-8").splitlines())
                for line, row in zip(act_contents, exp_data):

                    if row.rstrip() == line:
                        Messages.write_message("Actual row is :" + str(line))
                        Messages.write_message("success : Record as expected")
                    else:
                        assert (
                            row.rstrip() == line
                        ), f"Actual row is : {str(line)} Expected was : {row.rstrip()}\nUnsuccessful : expected record not found"
