import csv
import json
import os
from io import StringIO

import boto3
import pytest
from freezegun import freeze_time


from utils.database.models import JobStats, Errors


AWS_REGION = os.getenv("AWS_REGION")
LR_13_REGISTRATIONS_OUTPUT_BUCKET = os.getenv("LR_13_REGISTRATIONS_OUTPUT_BUCKET")
PDS_API_RETRIES = os.getenv("PDS_API_RETRIES")


def test_get_practice_patients(s3, lambda_handler):

    actual = lambda_handler.get_practice_patients("Y123452")

    expected = [
        {"nhs_number": "9000000009", "dispensing_flag": "1"},
        {"nhs_number": "1000000010", "dispensing_flag": "1"},
        {"nhs_number": "1100000011", "dispensing_flag": "1"},
    ]

    assert actual == expected


def test_get_pds_exclusive_registrations_with_no_existing_job_stats_ok(
    demographics, jobs, s3, lambda_handler
):

    lambda_handler.get_pds_exclusive_registrations("ABC123")

    only_on_pds_actual = JobStats.get("ABC123").OnlyOnPdsRecords

    assert only_on_pds_actual == 1


@pytest.mark.parametrize(
    "input_job,expected",
    [
        pytest.param(
            {"job_id": ""},
            {
                "status": "error",
                "message": "Unhandled error getting PDS registrations. JobId: 99999999-0909-0909-0909-999999999999",
            },
            id="Empty_Job_id",
        ),
        pytest.param(
            {"job_id": "blah"},
            {
                "status": "error",
                "message": "Unhandled error getting PDS registrations. JobId: blah",
            },
            id="Non-Existing Job_id",
        ),
    ],
)
def test_lambda_handler_for(
    demographics,
    jobstats,
    jobs,
    s3,
    lambda_handler,
    lambda_context,
    input_job,
    expected,
):
    result = lambda_handler.main(input_job, lambda_context)
    assert result["status"] == expected["status"]
    assert result["message"] == expected["message"]


@freeze_time("2020-02-01 13:40:00")
def test_get_pds_exclusive_registrations_ok(
    demographics, jobstats, jobs, s3, lambda_handler, lambda_context
):
    response = json.loads(lambda_handler.main({"job_id": "ABC123"}, lambda_context))

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
Smith,Jane,2010-10-22,9000000009,1 Trevelyan Square,Boar Lane,Leeds,West Yorkshire,,LS1 6AE,Mrs,female,2012-05-22"""
        )
    )

    assert list(actual) == list(expected)
