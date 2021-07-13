from getgauge.python import step
from getgauge.python import Messages
from tempfile import gettempdir
from .tf_aws_resources import get_aws_resources
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
AWS_RESOURCE = get_aws_resources()
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
EXPECED_CDD_DATA = os.path.join(ROOT, "data")

MOCK_PDS_DATA = AWS_RESOURCE["mock_pds_data"]["value"]
LR_12_LAMBDA = AWS_RESOURCE["lr_12_lambda"]["value"]
LR_10_STATE_FUNCTION_ARN = AWS_RESOURCE["lr_10_sfn_arn"]["value"]
LR_22_BUCKET = AWS_RESOURCE["lr_22_bucket"]["value"]
LR_13_BUCKET = AWS_RESOURCE["lr_13_bucket"]["value"]
DYNAMODB_DEMOG = AWS_RESOURCE["demographic_table"]["value"]
DYNAMODB_INFLIGHTS = AWS_RESOURCE["inflight_table"]["value"]
DYNAMODB_JOBS = AWS_RESOURCE["jobs_table"]["value"]
DYNAMODB_JOBSTATS = AWS_RESOURCE["jobs_stats_table"]["value"]


@step("prep step : connect to s3 buckets mock pds, lr-22 and upload data files for <lr-15> lambda")
def connect_to_s3_and_upload_mock_data_valid_scenario(lr_15_path):
    s3 = dev.client("s3", REGION_NAME)

    try:
        s3.upload_file(
            os.path.join(DATA, lr_15_path + "pds_api_data.csv"), MOCK_PDS_DATA, "pds_api_data.csv"
        )
        s3.upload_file(os.path.join(DATA, "LR_15/A82023.csv"), LR_22_BUCKET, "LR_15/A82023.csv")
        s3.upload_file(os.path.join(DATA, "LR_15/Y123451.csv"), LR_22_BUCKET, "LR_15/Y123451.csv")
        s3.upload_file(os.path.join(DATA, "LR_15/Y123452.csv"), LR_22_BUCKET, "LR_15/Y123452.csv")
        time.sleep(5)
        Messages.write_message("All PDS data related files Uploaded Successful")

    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step(
    "connect to lr-13 s3 bucket and ensure cdd csv file produced contains the expected consolidated records as in <expected_cdd_file>"
)
def assert_cdd_file_in_lr13(exp_cdd_datafile):
    exp_cdd_path = os.path.join(EXPECED_CDD_DATA, "LR_13/" + exp_cdd_datafile)

    s3 = dev.client("s3", REGION_NAME)
    result = s3.list_objects(Bucket=LR_13_BUCKET)
    with open(exp_cdd_path, "r") as exp_cdd_datafile:
        exp_cdd_data = sorted(exp_cdd_datafile)

        if result.get("Contents") != None:
            for key_items in result.get("Contents"):
                for filename in key_items.items():
                    if "-CDD-" in str(filename):
                        data = s3.get_object(Bucket=LR_13_BUCKET, Key=key_items.get("Key"))
                        act_contents = sorted(data["Body"].read().decode("utf-8").splitlines())
                        for line, row in zip(act_contents, exp_cdd_data):

                            if row.rstrip() == line:
                                Messages.write_message("Actual row is :" + str(line))
                                Messages.write_message("success : Record as expected")
                            else:
                                assert (
                                    row.rstrip() == line
                                ), f"Actual row is : {str(line)} Expected was : {row.rstrip()}\nUnsuccessful : expected record not found"
        else:
            assert False, "Result Contents is Null"
