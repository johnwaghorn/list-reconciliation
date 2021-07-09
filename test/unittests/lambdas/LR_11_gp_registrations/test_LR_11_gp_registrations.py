import csv
import os
from io import StringIO

import boto3
from freezegun import freeze_time


from utils.database.models import JobStats


AWS_REGION = os.getenv("AWS_REGION")
LR_13_REGISTRATIONS_OUTPUT_BUCKET = os.getenv("LR_13_REGISTRATIONS_OUTPUT_BUCKET")


@freeze_time("2020-02-01 13:40:00")
def test_get_gp_exclusive_registrations_ok(demographics, jobs, s3_bucket, jobstats, lambda_handler):
    response = lambda_handler.get_gp_exclusive_registrations("1")
    s3 = boto3.client("s3")

    elements = response["filename"].replace("s3://", "").split("/")
    bucket = elements.pop(0)
    key = "/".join(elements)

    assert JobStats.get("1").OnlyOnGpRecords == 3

    assert (
        response["filename"]
        == f"s3://{LR_13_REGISTRATIONS_OUTPUT_BUCKET}/1/Y12345-OnlyOnGP-20200201134000.csv"
    )

    actual = csv.reader(StringIO(s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode()))
    expected = csv.reader(
        StringIO(
            """SURNAME,FORENAMES,DOB,NHS NO.,ADD 1,ADD 2,ADD 3,ADD 4,ADD 5,POSTCODE,TITLE,SEX,STATUS,STATUS DATE
Corden,Steve,2004-05-01,1232,1 Park Street,,,,Manchester,LA1 234,Dr,0,Unmatched,2019-04-01
Davis,Jane,2004-05-01,1233,1 Park Street,,,,Manchester,LA1 234,Maj,1,Deducted Patient Match,2019-04-02
Frost,Chris,2004-05-01,1234,1 Park Street,,,,Manchester,LA1 234,Miss,2,Partnership Mismatch,2019-04-03"""
        )
    )

    assert list(actual) == list(expected)


@freeze_time("2020-02-01 13:50:00")
def test_get_gp_exclusive_registrations_no_diffs_ok(
    demographics, jobs, s3_bucket, jobstats, lambda_handler
):
    response = lambda_handler.get_gp_exclusive_registrations("2")
    s3 = boto3.client("s3")

    elements = response["filename"].replace("s3://", "").split("/")
    bucket = elements.pop(0)
    key = "/".join(elements)

    assert JobStats.get("2").OnlyOnGpRecords == 0

    assert (
        response["filename"]
        == f"s3://{LR_13_REGISTRATIONS_OUTPUT_BUCKET}/2/Y23456-OnlyOnGP-20200201135000.csv"
    )

    actual = csv.reader(StringIO(s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode()))
    expected = csv.reader(
        StringIO(
            """SURNAME,FORENAMES,DOB,NHS NO.,ADD 1,ADD 2,ADD 3,ADD 4,ADD 5,POSTCODE,TITLE,SEX,STATUS,STATUS DATE"""
        )
    )

    assert list(actual) == list(expected)
