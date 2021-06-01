from typing import Dict

import json
import os

import boto3
import requests

from utils.logger import log_dynamodb_error, success
from utils.models import Demographics
from utils.pds_api_service import get_pds_record, PDSAPIError


DEMOGRAPHIC_COMPARISON_LAMBDA = os.getenv("DEMOGRAPHIC_COMPARISON_LAMBDA")
AWS_REGION = os.getenv("AWS_REGION")


def pds_hydrate(nhs_number: str, job_id: str, patient_id: str) -> Dict[str, str]:
    """Populate an existing Demographics DynamoDB record with PDS data and trigger LR08.

    Args:
        nhs_number (str): NHS number of the patient to process.
        patient_id (str): Internal ID of the patient to process.
        job_id (str): ID of the job the comparison is being applied under.

    Returns:
        Dict: A result containing a status and message

    Raises:
        PDSAPIError: If the PDS FHIR API call fails, the error message contains
            the response content from the API call.
    """

    try:
        pds_record = get_pds_record(nhs_number, max_retries=5, backoff_factor=1)

    except requests.HTTPError as err:
        details = json.loads(err.response.content)["issue"][0]["details"]["coding"][0]
        msg = f"Error fetching PDS record for NHS number {nhs_number}, {details}"
        error_response = log_dynamodb_error(job_id, details["code"], msg)

        raise PDSAPIError(json.dumps(error_response)) from err

    record = Demographics.get(patient_id, job_id)

    record.update(
        actions=[
            Demographics.PDS_GpCode.set(pds_record["gp_code"]),
            Demographics.PDS_GpRegisteredDate.set(pds_record["gp_registered_date"]),
            Demographics.PDS_Surname.set(pds_record["surname"]),
            Demographics.PDS_Forenames.set(pds_record["forenames"]),
            Demographics.PDS_Titles.set(pds_record["title"]),
            Demographics.PDS_Gender.set(pds_record["gender"]),
            Demographics.PDS_DateOfBirth.set(pds_record["date_of_birth"]),
            Demographics.PDS_IsSensitive.set(pds_record["is_sensitive"]),
            Demographics.PDS_Address.set(pds_record["address"]),
            Demographics.PDS_PostCode.set(pds_record["postcode"]),
        ]
    )

    lambda_ = boto3.client("lambda", region_name=AWS_REGION)
    lambda_.invoke(
        FunctionName=DEMOGRAPHIC_COMPARISON_LAMBDA,
        InvocationType="Event",
        Payload=json.dumps({"patient_id": patient_id, "job_id": job_id}),
    )

    return success(
        f"Retrieved PDS data for NhsNumber: {nhs_number}, JobId: {job_id}, PatientId: {patient_id}"
    )
