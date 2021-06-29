import csv
import io
import json

from datetime import datetime
from typing import Dict, List

import os

import boto3
import botocore

from services.jobs import get_job
from utils import write_to_mem_csv, get_registration_filename, RegistrationType
from utils.logger import log_dynamodb_error, success, UNHANDLED_ERROR, LOG
from utils.database.models import Demographics, JobStats
from utils.pds_api_service import get_pds_record, PDSAPIError


LR_13_REGISTRATIONS_OUTPUT_BUCKET = os.getenv("LR_13_REGISTRATIONS_OUTPUT_BUCKET")
LR_22_PDS_PRACTICE_REGISTRATIONS_BUCKET = os.getenv("LR_22_PDS_PRACTICE_REGISTRATIONS_BUCKET")
PDS_API_RETRIES = os.getenv("PDS_API_RETRIES")


def get_practice_patients(practice_code: str) -> List[str]:
    """Get NHS numbers for patients registered at a practice from PDS extract.

    Args:
        practice_code (str): GP Practice code to get patient NHS numbers for.

    Returns:
        List[str]: List of NHS Numbers.
    """

    s3 = boto3.client("s3")
    key = f"{practice_code}.csv"
    bucket_path = f"{LR_22_PDS_PRACTICE_REGISTRATIONS_BUCKET}/{key}"
    LOG.info(f"Fetching {bucket_path}")

    try:
        obj = s3.get_object(Bucket=LR_22_PDS_PRACTICE_REGISTRATIONS_BUCKET, Key=key)
    except botocore.exceptions.ClientError:
        raise FileNotFoundError(f"File does not exist: {bucket_path}")

    contents = obj["Body"].read().decode()
    records = list(csv.DictReader(io.StringIO(contents)))

    return records


def lambda_handler(event, context):
    job_id = event["job_id"]

    try:
        return json.dumps(get_pds_exclusive_registrations(job_id))

    except Exception as err:
        msg = f"Unhandled error getting PDS registrations. JobId: {job_id or '99999999-0909-0909-0909-999999999999'}"
        error_response = log_dynamodb_error(job_id, UNHANDLED_ERROR, msg)

        raise Exception(error_response) from err


def get_pds_exclusive_registrations(job_id: str) -> Dict[str, str]:
    """Create a PDS-only registration differences file

    Args:
        job_id (str): Job ID.

    """

    practice_code = get_job(job_id).PracticeCode
    practice_patients = get_practice_patients(practice_code)

    rows = []

    job_nhs_numbers = [r.NhsNumber for r in Demographics.JobIdIndex.query(job_id)]

    for patient in practice_patients:
        nhs_number = patient["nhs_number"]

        if nhs_number not in job_nhs_numbers:
            try:
                pds_record = get_pds_record(nhs_number, max_retries=PDS_API_RETRIES)

            except PDSAPIError as err:
                msg = f"Error fetching PDS record for NHS number {nhs_number}, {err.details}"
                error_response = log_dynamodb_error(job_id, err.details["code"], msg)

                raise PDSAPIError(json.dumps(error_response)) from err

            rows.append(
                {
                    "SURNAME": pds_record["surname"],
                    "FORENAMES": " ".join(pds_record["forenames"]),
                    "DOB": pds_record["date_of_birth"],
                    "NHS NO.": nhs_number,
                    "ADD 1": pds_record["address"][0],
                    "ADD 2": pds_record["address"][1],
                    "ADD 3": pds_record["address"][2],
                    "ADD 4": pds_record["address"][3],
                    "ADD 5": pds_record["address"][4],
                    "POSTCODE": pds_record["postcode"],
                    "TITLE": ", ".join(pds_record["title"]),
                    "SEX": pds_record["gender"],
                    "DATE ACCEPT.": datetime.strptime(
                        pds_record["gp_registered_date"], "%Y-%m-%d"
                    ).date(),
                }
            )

    try:
        job_stat = JobStats.get(job_id)

    except JobStats.DoesNotExist:
        JobStats(job_id, OnlyOnPdsRecords=len(rows)).save()

    else:
        job_stat.update(actions=[JobStats.OnlyOnPdsRecords.set(len(rows))])

    filename = get_registration_filename(practice_code, RegistrationType.PDS)

    header = [
        "SURNAME",
        "FORENAMES",
        "DOB",
        "NHS NO.",
        "ADD 1",
        "ADD 2",
        "ADD 3",
        "ADD 4",
        "ADD 5",
        "POSTCODE",
        "TITLE",
        "SEX",
        "DATE ACCEPT.",
    ]
    stream = write_to_mem_csv(rows, header)

    key = f"{job_id}/{filename}"
    boto3.client("s3").put_object(
        Body=stream.getvalue(),
        Bucket=LR_13_REGISTRATIONS_OUTPUT_BUCKET,
        Key=key,
    )

    out = success("Got PDS-only registrations")
    out.update(filename=f"s3://{LR_13_REGISTRATIONS_OUTPUT_BUCKET}/{key}")

    return out
