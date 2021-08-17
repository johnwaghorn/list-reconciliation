import os

import boto3

AWS_REGION = os.environ.get("AWS_REGION")
MESH_BUCKET = os.getenv("MESH_BUCKET")


def test_send_list_rec_results_ok(
    lambda_handler,
    lambda_context,
    jobstats,
    jobs,
    demographicsdifferences,
    s3,
    ssm,
    mesh_ssm,
    email_ssm,
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
