import json
import os

from freezegun import freeze_time

import boto3
import pytest

from lambdas.LR_15_process_demo_diffs.process_demographic_differences import (
    process_demographic_differences,
)
from services.jobs import JobNotFound
from utils.database.models import JobStats, Jobs


MESH_SEND_BUCKET = os.getenv("MESH_SEND_BUCKET")


@freeze_time("2020-04-06 13:40:00+01:00")
def test_process_demographic_differences(
    demographics, demographics_differences, jobstats, jobs, s3
):
    job_id = "7b207bdb-2937-4e17-a1a9-57a2bbf3e358"
    response = process_demographic_differences(job_id)

    expected = {
        "system": {
            "name": "GP List Reconciliation",
            "source": "GP System",
            "patientId": "c7c8b6e2-8ce2-4bc6-804e-3d7ac4054bd1",
            "jobId": job_id,
        },
        "patient": {
            "nhsNumber": "1234567890",
            "gpData": {
                "birthDate": "20020101",
                "gender": "1",
                "name": {
                    "given": "JOHN",
                    "family": "JONES",
                    "previousFamily": "",
                    "prefix": "MR",
                },
                "address": {
                    "line1": "FLAT A",
                    "line2": "THE STREET",
                    "line3": "",
                    "line4": "EAST",
                    "line5": "",
                },
                "postalCode": "E1   1AA",
                "generalPractitionerOds": "Y123452",
            },
            "pdsData": {
                "scn": "1",
                "birthDate": "2002-02-01",
                "gender": "male",
                "name": [
                    {
                        "given": ["JOHN"],
                        "family": "JOHNSON",
                        "prefix": ["MR"],
                    }
                ],
                "address": ["FLAT A", "THE STREET", "EAST"],
                "postalCode": "E1   1ZZ",
                "generalPractitionerOds": "Y123452",
            },
        },
        "differences": [
            {
                "ruleId": "MN-BR-SN-01",
                "guidance": "Manual Validation",
            },
            {
                "ruleId": "MN-BR-DB-01",
                "guidance": "Manual Validation",
            },
            {
                "ruleId": "MN-BR-AD-02",
                "guidance": "Manual Validation",
            },
        ],
    }

    s3 = boto3.client("s3")
    actual = json.loads(
        s3.get_object(
            Bucket=MESH_SEND_BUCKET,
            Key="7b207bdb-2937-4e17-a1a9-57a2bbf3e358/Y123452-WIP-7b207bdb-2937-4e17-a1a9-57a2bbf3e358-1234567890-20200406134000.json",
        )["Body"]
        .read()
        .decode()
    )

    assert actual == expected

    job = Jobs.get(job_id, "Y123452")
    jobstats = JobStats.get(job_id)

    assert job.StatusId == "3"
    assert jobstats.PdsUpdatedRecords == 0
    assert jobstats.GpUpdatedRecords == 0
    assert jobstats.HumanValidationRecords == 3
    assert jobstats.PotentialPdsUpdateRecords == 0
    assert jobstats.PotentialGpUpdateRecords == 0

    assert response == {
        "status": "success",
        "message": f"Demographic differences processed for JobId {job_id}",
        "filenames": [
            f"s3://{MESH_SEND_BUCKET}/7b207bdb-2937-4e17-a1a9-57a2bbf3e358/Y123452-WIP-7b207bdb-2937-4e17-a1a9-57a2bbf3e358-1234567890-20200406134000.json"
        ],
    }


def test_process_demographic_differences_no_diffs_for_job(
    demographics, demographics_differences, jobstats, jobs, s3
):
    with pytest.raises(JobNotFound):
        process_demographic_differences("ABC123")
