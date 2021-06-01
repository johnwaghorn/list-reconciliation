import json
import os

import boto3

from utils.logger import log_dynamodb_error, UNHANDLED_ERROR
from utils.pds_api_service import PDSAPIError

AWS_REGION = os.getenv("AWS_REGION")


def lambda_handler(event, context):
    from pds_hydrate import pds_hydrate

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
