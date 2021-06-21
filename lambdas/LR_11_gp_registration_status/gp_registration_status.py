import json
import os

import boto3

from utils import write_to_mem_csv, get_registration_filename, RegistrationType
from utils.logger import success, Success, log_dynamodb_error, UNHANDLED_ERROR
from utils.models import Demographics, Jobs, JobStats
from utils.registration_status import GPRegistrationStatus


LR_13_REGISTRATIONS_OUTPUT_BUCKET = os.getenv("LR_13_REGISTRATIONS_OUTPUT_BUCKET")


def lambda_handler(event, context):
    try:
        job_id = json.loads(event["job_id"])

    except json.JSONDecodeError:
        job_id = event["job_id"]

    try:
        return json.dumps(get_gp_exclusive_registrations(job_id))

    except Exception as err:
        msg = f"Unhandled error getting gp registrations. JobId: {job_id}"
        error_response = log_dynamodb_error(job_id, UNHANDLED_ERROR, msg)

        raise type(err)(error_response) from err


def get_gp_exclusive_registrations(job_id: str) -> Success:
    """Create a GP-only registration differences file

    Args:
        job_id (str): Job ID.

    """
    practice_code = Jobs.query(job_id).next().PracticeCode

    results = Demographics.JobIdIndex.query(
        job_id,
        filter_condition=Demographics.GP_RegistrationStatus != GPRegistrationStatus.MATCHED.value,
    )

    rows = [
        {
            "SURNAME": result.GP_Surname,
            "FORENAMES": result.GP_Forenames,
            "DOB": result.GP_DateOfBirth,
            "NHS NO.": result.NhsNumber,
            "ADD 1": result.GP_AddressLine1,
            "ADD 2": result.GP_AddressLine2,
            "ADD 3": result.GP_AddressLine3,
            "ADD 4": result.GP_AddressLine4,
            "ADD 5": result.GP_AddressLine5,
            "POSTCODE": result.GP_PostCode,
            "TITLE": result.GP_Title,
            "SEX": result.GP_Gender,
            "STATUS": result.GP_RegistrationStatus,
            "STATUS DATE": result.PDS_GpRegisteredDate,
        }
        for result in results
    ]

    try:
        job_stat = JobStats.get(job_id)

    except JobStats.DoesNotExist:
        JobStats(job_id, OnlyOnGpRecords=len(rows)).save()

    else:
        job_stat.update(actions=[JobStats.OnlyOnGpRecords.set(len(rows))])

    filename = get_registration_filename(practice_code, RegistrationType.GP)

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
        "STATUS",
        "STATUS DATE",
    ]
    stream = write_to_mem_csv(rows, header)

    key = f"{practice_code}/{filename}"
    boto3.client("s3").put_object(
        Body=stream.getvalue(),
        Bucket=LR_13_REGISTRATIONS_OUTPUT_BUCKET,
        Key=key,
    )

    out = success(f"Got {len(rows)} GP-only registrations")
    out.update(filename=f"s3://{LR_13_REGISTRATIONS_OUTPUT_BUCKET}/{key}")

    return out
