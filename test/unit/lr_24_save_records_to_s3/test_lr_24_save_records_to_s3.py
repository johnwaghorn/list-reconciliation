import json
import os

import boto3
import pytest

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "..", "_data", "unit")

LR_06_BUCKET = os.environ.get("LR_06_BUCKET")
REGION_NAME = os.environ.get("AWS_REGION")


def test_save_records_to_s3_saves_records(s3, lambda_handler, lambda_context, records):
    event = {
        "id_cols": ["job_id", "practice_code", "id"],
        "destination_bucket": LR_06_BUCKET,
        "source": "TEST",
        "records": [json.dumps(record) for record in records],
    }

    response = lambda_handler.main(event=event, context=lambda_context)

    expected = "LR24 Lambda application stopped"

    assert response["message"] == expected

    s3_client = boto3.client("s3")

    files = [obj["Key"] for obj in s3_client.list_objects_v2(Bucket=LR_06_BUCKET)["Contents"]]

    actual = [
        json.loads(
            s3_client.get_object(Bucket=LR_06_BUCKET, Key=file)["Body"].read().decode("utf-8")
        )
        for file in files
    ]

    expected = records

    assert sorted(actual, key=lambda x: x["NHS_NUMBER"]) == sorted(
        expected, key=lambda x: x["NHS_NUMBER"]
    )


def test_save_records_to_s3_raises_Exception(s3, lambda_handler, lambda_context, records):
    event = {
        "id_cols": ["col_doesnt_exist", "practice_code", "id"],
        "destination_bucket": LR_06_BUCKET,
        "source": "TEST",
        "records": [json.dumps(record) for record in records],
    }

    with pytest.raises(KeyError):
        lambda_handler.main(event=event, context=lambda_context)
