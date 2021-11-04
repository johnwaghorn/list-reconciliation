import json

import boto3
import pytest
from freezegun import freeze_time

from .conftest import MESH_BUCKET, MOCK_OUTBOX


def test_lr14_handler_invalid_event_raises_key_error(lambda_handler, lambda_context):
    event = {"error": "error"}
    with pytest.raises(KeyError):
        lambda_handler.main(event, lambda_context)


def test_lr14_send_list_rec_results_ok(
    lambda_handler,
    lambda_context,
    jobstats,
    jobs,
    demographicsdifferences,
    ssm,
    mesh_ssm,
    upload_lr13_files,
    create_mesh_bucket,
    create_outbox_bucket,
):
    event = {"job_id": "7b207bdb-2937-4e17-a1a9-57a2bbf3e358"}
    response = lambda_handler.main(event, lambda_context)

    expected_title = "PDS Comparison run at 15:48:37 on 27/05/2021 against Practice: Y123452 - Y123452.E1A - Registrations Output"
    expected_body = """The GP file: Y123452.E1A has been compared to PDS at 15:48:37 on 27/05/2021

3 patient records were found on PDS, that were not in the GP file.

5 patient records were found in the GP file, that are not associated to this GP in PDS.

The comparison run has also discovered 3 discrepancies that have generated 1 work
item/s to resolve, with 0 record/s being automatically updated in PDS and
3 record/s being provided for the GP Practice to review and update.

The files generated can be found in your MESH mailbox:
    • cdd.csv
    • gponly.csv
    • pdsonly.csv

For support reference, the Reconciliation Run Id associated to this email is: 7b207bdb-2937-4e17-a1a9-57a2bbf3e358"""

    actual_files = [
        obj["Key"]
        for obj in boto3.client("s3").list_objects_v2(
            Bucket=MESH_BUCKET, Prefix="outbound_X26OT181TEST_to_X26OT188TEST"
        )["Contents"]
    ]

    assert sorted(actual_files) == sorted(
        [
            "outbound_X26OT181TEST_to_X26OT188TEST/gponly.csv",
            "outbound_X26OT181TEST_to_X26OT188TEST/pdsonly.csv",
            "outbound_X26OT181TEST_to_X26OT188TEST/cdd.csv",
        ]
    )

    assert response["email_subject"] == expected_title
    assert response["email_body"] == expected_body


def test_lr14_result_is_sent_to_outbox(
    lambda_handler,
    lambda_context,
    jobstats,
    jobs,
    demographicsdifferences,
    ssm,
    mesh_ssm,
    upload_lr13_files,
    create_mesh_bucket,
    create_outbox_bucket,
):
    event = {"job_id": "7b207bdb-2937-4e17-a1a9-57a2bbf3e358"}
    lambda_handler.main(event, lambda_context)

    client = boto3.client("s3")
    bucket_objs = client.list_objects_v2(Bucket=MOCK_OUTBOX)
    for obj in bucket_objs.get("Contents", []):
        key = obj["Key"]

    expected_key_len = 41
    # len(uuid4 + ".json")
    actual_key_len = len(key)
    assert actual_key_len == expected_key_len


@freeze_time("2021-09-27 11:20:24")
def test_lr14_alert_in_outbox(
    lambda_handler,
    lambda_context,
    jobstats,
    jobs,
    demographicsdifferences,
    ssm,
    mesh_ssm,
    upload_lr13_files,
    create_mesh_bucket,
    create_outbox_bucket,
):

    event = {"job_id": "7b207bdb-2937-4e17-a1a9-57a2bbf3e358"}
    lambda_handler.main(event, lambda_context)

    # Grab generated uuid/key/filename from S3
    client = boto3.client("s3")
    bucket_objs = client.list_objects_v2(Bucket=MOCK_OUTBOX)
    for obj in bucket_objs.get("Contents", []):
        key = obj["Key"]

    # Get object of uuid and load as json
    file = client.get_object(Bucket=MOCK_OUTBOX, Key=str(key))
    json_content = json.loads(file["Body"].read().decode("utf-8"))

    expected_subject = "PDS Comparison run at 15:48:37 on 27/05/2021 against Practice: Y123452 - Y123452.E1A - Registrations Output"
    expected_body = "The GP file: Y123452.E1A has been compared to PDS at 15:48:37 on 27/05/2021\n\n3 patient records were found on PDS, that were not in the GP file.\n\n5 patient records were found in the GP file, that are not associated to this GP in PDS.\n\nThe comparison run has also discovered 3 discrepancies that have generated 1 work\nitem/s to resolve, with 0 record/s being automatically updated in PDS and\n3 record/s being provided for the GP Practice to review and update.\n\nThe files generated can be found in your MESH mailbox:\n    • cdd.csv\n    • gponly.csv\n    • pdsonly.csv\n\nFor support reference, the Reconciliation Run Id associated to this email is: 7b207bdb-2937-4e17-a1a9-57a2bbf3e358"
    assert json_content["service"].lower() == "lr-14"
    assert json_content["to"] == ["test@example.com"]
    assert json_content["timestamp"] == "20210927112024"
    assert json_content["subject"] == expected_subject
    assert json_content["body"] == expected_body
