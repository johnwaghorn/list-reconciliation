from unittest import mock

import json
import os

from moto import mock_s3

import boto3
import pytest

from utils.pds_api_service import get_mock_pds_record, get_pds_fhir_record

PDS_API_URL = os.getenv("PDS_API_URL")
AWS_REGION = os.getenv("AWS_REGION")

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "..", "lambdas", "data")


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.content = json_data
            self.status_code = status_code

        def raise_for_status(self):
            if self.status_code >= 300:
                raise Exception(self.status_code)

    return MockResponse(
        json.dumps(json.load(open(os.path.join(DATA, "pds_fhir_api_response.json")))), 200
    )


@pytest.fixture
def s3():
    with mock_s3():
        s3 = boto3.client("s3", region_name=AWS_REGION)
        bucket = PDS_API_URL.replace("s3://", "").split("/")[0]
        s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )
        s3.upload_file(os.path.join(DATA, "pds_api_data.csv"), bucket, "pds_api_data.csv")
        yield


@mock.patch("requests.Session.get", side_effect=mocked_requests_get)
def test_get_pds_fhir_record(pds_url):

    actual = get_pds_fhir_record(pds_url, "9000000009")

    expected = {
        "surname": "Smith",
        "forenames": ["Jane"],
        "title": ["Mrs"],
        "gender": "female",
        "date_of_birth": "2010-10-22",
        "address": ["1 Trevelyan Square", "Boar Lane", "City Centre", "Leeds", "West Yorkshire"],
        "postcode": "LS1 6AE",
        "gp_code": "Y12345",
        "gp_registered_date": "2020-01-01",
        "sensitive": "U",
        "version": "2",
    }

    assert actual == expected


def test_get_pds_mock_record(s3):

    actual = get_mock_pds_record(PDS_API_URL, "9000000009")

    expected = {
        "surname": "Smith",
        "forenames": ["Jane"],
        "title": ["Mrs"],
        "gender": "female",
        "date_of_birth": "2010-10-22",
        "address": ["1 Trevelyan Square", "Boar Lane", "City Centre", "Leeds", "West Yorkshire"],
        "postcode": "LS1 6AE",
        "gp_code": "Y123452",
        "gp_registered_date": "2012-05-22",
        "sensitive": "U",
        "version": "1",
    }

    assert actual == expected
