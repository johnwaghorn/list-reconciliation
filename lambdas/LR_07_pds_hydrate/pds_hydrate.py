import json
import os

import boto3

from utils.logger import log_dynamodb_error, success, Success, UNHANDLED_ERROR
from utils.database.models import Demographics
from utils.pds_api_service import get_pds_record, PDSAPIError
from utils.registration_status import get_gp_registration_status, GPRegistrationStatus

DEMOGRAPHIC_COMPARISON_LAMBDA = os.getenv("DEMOGRAPHIC_COMPARISON_LAMBDA")
AWS_REGION = os.getenv("AWS_REGION")


def lambda_handler(event, context):
    record = event["Records"][0]
    body = json.loads(record["body"])
    job_id = str(body["job_id"])
    patient_id = str(body["patient_id"])
    nhs_number = str(body["nhs_number"])

    try:
        queue_arn = record.get("eventSourceARN")

        if queue_arn:
            account_id, queue_name = queue_arn.split(":")[-2:]
            sqs = boto3.client("sqs")

            sqs.delete_message(
                QueueUrl=sqs.get_queue_url(QueueName=queue_name, QueueOwnerAWSAccountId=account_id)[
                    "QueueUrl"
                ],
                ReceiptHandle=record["receiptHandle"],
            )

        return json.dumps(pds_hydrate(nhs_number, job_id, patient_id))

    except PDSAPIError:
        raise

    except Exception as err:
        msg = f"Unhandled error patient_id: {patient_id} nhs_number: {nhs_number}"
        error_response = log_dynamodb_error(job_id, UNHANDLED_ERROR, msg)

        raise type(err)(error_response) from err


def pds_hydrate(nhs_number: str, job_id: str, patient_id: str) -> Success:
    """Populate an existing Demographics DynamoDB record with PDS data and trigger LR08.

    Args:
        nhs_number (str): NHS number of the patient to process.
        patient_id (str): Internal ID of the patient to process.
        job_id (str): ID of the job the comparison is being applied under.

    Returns:
        Success

    Raises:
        PDSAPIError: If the PDS FHIR API call fails, the error message contains
            the response content from the API call.
    """

    try:
        pds_record = get_pds_record(nhs_number, max_retries=5, backoff_factor=1)

    except PDSAPIError as err:
        msg = f"Error fetching PDS record for NHS number {nhs_number}, {err.details}"
        error_response = log_dynamodb_error(job_id, err.details["code"], msg)

        raise PDSAPIError(json.dumps(error_response)) from err

    record = Demographics.get(patient_id, job_id)

    status = get_gp_registration_status(record.GP_GpCode, pds_record)

    if status == GPRegistrationStatus.UNMATCHED.value:

        record.update(
            actions=[
                Demographics.IsComparisonCompleted.set(True),
                Demographics.GP_RegistrationStatus.set(status),
            ]
        )

        return success(
            f"PDS data not found for NhsNumber: {nhs_number}, JobId: {job_id}, PatientId: {patient_id}"
        )

    record.update(
        actions=[
            Demographics.PDS_GpCode.set(pds_record["gp_code"]),
            Demographics.PDS_GpRegisteredDate.set(pds_record["gp_registered_date"]),
            Demographics.PDS_Surname.set(pds_record["surname"]),
            Demographics.PDS_Forenames.set(pds_record["forenames"]),
            Demographics.PDS_Titles.set(pds_record["title"]),
            Demographics.PDS_Gender.set(pds_record["gender"]),
            Demographics.PDS_DateOfBirth.set(pds_record["date_of_birth"]),
            Demographics.PDS_Sensitive.set(pds_record["sensitive"]),
            Demographics.PDS_Address.set(pds_record["address"]),
            Demographics.PDS_PostCode.set(pds_record["postcode"]),
            Demographics.GP_RegistrationStatus.set(status),
            Demographics.PDS_Version.set(pds_record["version"]),
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
