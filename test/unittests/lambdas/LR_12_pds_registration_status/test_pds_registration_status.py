from io import StringIO

import csv
import json
import os

from freezegun import freeze_time

import boto3
import pytest

from lambdas.LR_12_pds_registration_status.pds_registration_status import (
    get_pds_exclusive_registrations,
    get_practice_patients,
    lambda_handler,
)
from utils.models import JobStats, Errors

AWS_REGION = os.getenv("AWS_REGION")
LR_13_REGISTRATIONS_OUTPUT_BUCKET = os.getenv("LR_13_REGISTRATIONS_OUTPUT_BUCKET")


def test_get_practice_patients(s3):
    actual = get_practice_patients("Y123452")

    expected = [
        {"nhs_number": "9000000009", "dispensing_flag": "1"},
        {"nhs_number": "1000000010", "dispensing_flag": "1"},
        {"nhs_number": "1100000011", "dispensing_flag": "1"},
    ]

    assert actual == expected


def test_get_pds_exclusive_registrations_with_no_existing_job_stats_ok(demographics, jobs, s3):
    get_pds_exclusive_registrations("ABC123")

    only_on_pds_actual = JobStats.get("ABC123").OnlyOnPdsRecords

    assert only_on_pds_actual == 1


def test_lambda_handler_empty_string_raises_JobNotFound(demographics, jobstats, jobs, s3):
    with pytest.raises(Exception):
        lambda_handler({"job_id": ""}, None)

    error = [e for e in Errors.scan()][0]

    assert error.JobId == "99999999-0909-0909-0909-999999999999"
    assert error.Name == "UNHANDLED_ERROR"
    assert (
        error.Description
        == "Unhandled error getting PDS registrations. JobId: 99999999-0909-0909-0909-999999999999"
    )


def test_lambda_handler_nonexistent_job_raises_JobNotFound(demographics, jobstats, jobs, s3):
    with pytest.raises(Exception):
        lambda_handler({"job_id": "blah"}, None)

    error = [e for e in Errors.scan()][0]

    assert error.JobId == "blah"
    assert error.Name == "UNHANDLED_ERROR"
    assert error.Description == "Unhandled error getting PDS registrations. JobId: blah"


@freeze_time("2020-02-01 13:40:00")
def test_get_pds_exclusive_registrations_ok(demographics, jobstats, jobs, s3):
    response = json.loads(lambda_handler({"job_id": "ABC123"}, None))

    s3 = boto3.client("s3")

    elements = response["filename"].replace("s3://", "").split("/")
    bucket = elements.pop(0)
    key = "/".join(elements)

    only_on_pds_actual = JobStats.get("ABC123").OnlyOnPdsRecords

    assert only_on_pds_actual == 1

    assert (
        response["filename"]
        == f"s3://{LR_13_REGISTRATIONS_OUTPUT_BUCKET}/ABC123/Y123452-OnlyOnPDS-20200201134000.csv"
    )

    actual = csv.reader(StringIO(s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode()))
    expected = csv.reader(
        StringIO(
            """SURNAME,FORENAMES,DOB,NHS NO.,ADD 1,ADD 2,ADD 3,ADD 4,ADD 5,POSTCODE,TITLE,SEX,DATE ACCEPT.
Smith,Jane,2010-10-22,9000000009,1 Trevelyan Square,Boar Lane,City Centre,Leeds,West Yorkshire,LS1 6AE,Mrs,female,2012-05-22"""
        )
    )

    assert list(actual) == list(expected)
