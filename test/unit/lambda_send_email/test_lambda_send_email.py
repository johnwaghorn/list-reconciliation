import boto3
import pytest

from .conftest import EMAIL_BUCKET, EMAIL_FILE


def test_send_email_raises_key_error(lambda_handler, lambda_context):
    event = {"error": "error"}
    with pytest.raises(KeyError):
        lambda_handler.main(event, lambda_context)


def test_send_email_ok(lambda_handler, lambda_context, upload_email_file):

    event = {
        "Records": [
            {
                "s3": {
                    "object": {"key": f"{EMAIL_FILE}"},
                    "bucket": {"name": f"{EMAIL_BUCKET}"},
                },
            }
        ]
    }
    response = lambda_handler.main(event, lambda_context)

    expected_subject = "testing lambda_send_email"
    expected_body = (
        """Lorem Ipsum is simply dummy text of the printing and typesetting industry"""
    )

    assert response["email_subject"] == expected_subject
    assert response["email_body"] == expected_body


def test_file_cleanup_ok(
    lambda_handler,
    lambda_context,
    upload_email_file,
):

    # Ensure email file is in s3 before sending email
    client = boto3.client("s3")
    bucket_objs = client.list_objects_v2(Bucket=EMAIL_BUCKET)
    for obj in bucket_objs.get("Contents", []):
        key = obj["Key"]

    assert EMAIL_FILE == key

    event = {
        "Records": [
            {
                "s3": {
                    "object": {"key": f"{EMAIL_FILE}"},
                    "bucket": {"name": f"{EMAIL_BUCKET}"},
                },
            }
        ]
    }

    # Send email file from S3 and cleanup file
    lambda_handler.main(event, lambda_context)

    # List objects from S3 and assert the same file has been removed
    bucket_objs = client.list_objects_v2(Bucket=EMAIL_BUCKET)
    assert EMAIL_FILE not in str(bucket_objs)
