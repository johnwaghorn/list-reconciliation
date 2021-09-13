import csv
import json
import os
from io import StringIO

import boto3
import pytest
from database.models import JobStats
from freezegun import freeze_time
from jobs.jobs import JobNotFound

MESH_BUCKET = os.getenv("MESH_BUCKET")
LR_13_REGISTRATIONS_OUTPUT_BUCKET = os.getenv("LR_13_REGISTRATIONS_OUTPUT_BUCKET")
JOBID = "7b207bdb-2937-4e17-a1a9-57a2bbf3e358"


@freeze_time("2020-04-06 13:40:00+00:00")
def test_process_demographic_differences(
    demographics, demographics_differences, jobstats, jobs, s3, lambda_handler, ssm, mesh_ssm
):
    lambda_handler.job_id = JOBID
    lambda_handler.log_object.set_internal_id(JOBID)
    lambda_handler.lr13_bucket = LR_13_REGISTRATIONS_OUTPUT_BUCKET

    actual_response = lambda_handler.process_demographic_differences()

    expected = {
        "system": {
            "name": "GP List Reconciliation",
            "source": "GP System",
            "patientId": "c7c8b6e2-8ce2-4bc6-804e-3d7ac4054bd1",
            "jobId": JOBID,
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
                "security": "U",
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
            Bucket=MESH_BUCKET,
            Key="outbound_X26OT178TEST_to_INTERNALSPINE/Y123452-WIP-7b207bdb-2937-4e17-a1a9-57a2bbf3e358-1234567890-20200406134000.json",
        )["Body"]
        .read()
        .decode()
    )

    assert actual == expected

    actual_csv = csv.reader(
        StringIO(
            s3.get_object(
                Bucket=LR_13_REGISTRATIONS_OUTPUT_BUCKET,
                Key=f"7b207bdb-2937-4e17-a1a9-57a2bbf3e358/Y123452-CDD-20200406134000.csv",
            )["Body"]
            .read()
            .decode()
        )
    )

    expected_csv = csv.reader(
        StringIO(
            """nhsNumber,gp_birthDate,gp_gender,gp_name_given,gp_name_family,gp_name_previousFamily,gp_name_prefix,gp_address_line1,gp_address_line2,gp_address_line3,gp_address_line4,gp_address_line5,gp_postalCode,gp_generalPractitionerOds,pds_scn,pds_security,pds_birthDate,pds_gender,pds_name_given,pds_name_family,pds_name_prefix,pds_address,pds_postalCode,pds_generalPractitionerOds,ruleId,guidance
1234567890,20020101,1,JOHN,JONES,,MR,FLAT A,THE STREET,,EAST,,E1   1AA,Y123452,1,U,2002-02-01,male,JOHN,JOHNSON,MR,"FLAT A,THE STREET,EAST",E1   1ZZ,Y123452,MN-BR-SN-01,Manual Validation
1234567890,20020101,1,JOHN,JONES,,MR,FLAT A,THE STREET,,EAST,,E1   1AA,Y123452,1,U,2002-02-01,male,JOHN,JOHNSON,MR,"FLAT A,THE STREET,EAST",E1   1ZZ,Y123452,MN-BR-DB-01,Manual Validation
1234567890,20020101,1,JOHN,JONES,,MR,FLAT A,THE STREET,,EAST,,E1   1AA,Y123452,1,U,2002-02-01,male,JOHN,JOHNSON,MR,"FLAT A,THE STREET,EAST",E1   1ZZ,Y123452,MN-BR-AD-02,Manual Validation
"""
        )
    )

    assert list(actual_csv) == list(expected_csv)

    jobstats = JobStats.get(JOBID)

    assert jobstats.PdsUpdatedRecords == 0
    assert jobstats.GpUpdatedRecords == 0
    assert jobstats.HumanValidationRecords == 3
    assert jobstats.PotentialPdsUpdateRecords == 0
    assert jobstats.PotentialGpUpdateRecords == 0
    assert jobstats.TotalRecords == 1

    expected_response = {
        "status": "success",
        "message": f"LR15 Lambda application stopped for jobId='{JOBID}'",
        "work_items": [
            f"s3://{MESH_BUCKET}/outbound_X26OT178TEST_to_INTERNALSPINE/Y123452-WIP-7b207bdb-2937-4e17-a1a9-57a2bbf3e358-1234567890-20200406134000.json"
        ],
        "summary": f"s3://{LR_13_REGISTRATIONS_OUTPUT_BUCKET}/7b207bdb-2937-4e17-a1a9-57a2bbf3e358/Y123452-CDD-20200406134000.csv",
        "internal_id": JOBID,
    }

    assert actual_response == expected_response


def test_process_demographic_differences_no_diffs_for_job(
    demographics, demographics_differences, jobstats, jobs, s3, lambda_handler, mesh_ssm
):
    lambda_handler.job_id = "ABC123"
    lambda_handler.lr13_bucket = LR_13_REGISTRATIONS_OUTPUT_BUCKET

    with pytest.raises(JobNotFound):
        lambda_handler.process_demographic_differences()
