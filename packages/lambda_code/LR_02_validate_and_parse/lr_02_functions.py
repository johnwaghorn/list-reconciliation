import json
from typing import Dict
from uuid import uuid4

import boto3
from botocore.client import BaseClient
from pynamodb.exceptions import PynamoDBConnectionError, PutError
from retrying import retry
from spine_aws_common.logger import Logger

from gp_file_parser.file_name_parser import InvalidFilename
from gp_file_parser.parser import InvalidGPExtract, parse_gp_extract_file_s3
from gp_file_parser.utils import empty_string
from utils.datetimezone import get_datetime_now
from utils.logger import log_dynamodb_error, success
from utils.database.models import Jobs, InFlight, Demographics

INBOUND_PREFIX = "inbound/"
FAILED_PREFIX = "fail/"
PASSED_PREFIX = "pass/"
RETRY_PREFIX = "retry/"


class SQSError(Exception):
    pass


class ValidateAndParse:
    def __init__(
        self, upload_key: str, job_id: str, lambda_env: Dict[str, str], logger: Logger
    ):
        self.upload_key = upload_key
        self.job_id = job_id
        self.lambda_env = lambda_env
        self.logger = logger

    def create_client(self, service: str) -> BaseClient:
        return boto3.client(
            service,
            region_name=self.lambda_env["AWS_REGION"],
            aws_access_key_id=self.lambda_env["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=self.lambda_env["AWS_SECRET_ACCESS_KEY"],
            aws_session_token=self.lambda_env["AWS_SESSION_TOKEN"],
        )

    def validate_and_process_extract(self) -> success:
        """Handler to process and validate an uploaded S3 object containing a GP flat
            file extract

        Returns:
            success: A dict result containing a status and message
        """

        upload_filename = self.upload_key.replace(INBOUND_PREFIX, "")
        upload_date = get_datetime_now()

        self.logger.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR02.Lambda",
                "level": "INFO",
                "message": f"{self.upload_key} validation process begun at {upload_date}",
            },
        )

        try:
            records, gp_ha_cipher = parse_gp_extract_file_s3(
                self.lambda_env["AWS_S3_REGISTRATION_EXTRACT_BUCKET"],
                self.upload_key,
                upload_date,
            )

            return self.handle_validated_records(upload_filename, gp_ha_cipher, records)

        except (AssertionError, InvalidGPExtract, InvalidFilename) as exc:
            message = self.process_invalid_message(exc)

            self.handle_extract(FAILED_PREFIX, message)

            msg = f"Handled error for invalid file upload: {upload_filename}"
            log_dynamodb_error(self.logger, self.job_id, "HANDLED_ERROR", msg)

            return success(
                f"Invalid file {upload_filename} handled successfully for Job: {self.job_id}"
            )

    def handle_validated_records(
        self, upload_filename: str, gp_ha_cipher: str, records: list
    ) -> success:
        """Handler to process validated patient records

        Args:
            upload_filename (str): Filename of uploaded GP extract
            gp_ha_cipher (str): HA cypher of GP extract
            records (list): List of validated record dicts

        Returns:
            success: A dict result containing a status and message
        """

        num_of_records = len(records)
        self.logger.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR02.Lambda",
                "level": "INFO",
                "message": f"{upload_filename} results collected: {num_of_records} records",
            },
        )

        try:
            records = self.write_to_dynamodb(
                gp_ha_cipher, upload_filename, records, num_of_records
            )
            self.logger.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR02.Lambda",
                    "level": "INFO",
                    "message": f"Batch write to demographics was successful for Job: {self.job_id}",
                },
            )

        except (PynamoDBConnectionError, PutError) as exc:
            self.handle_extract(RETRY_PREFIX)

            log_dynamodb_error(
                self.log_object, self.logger, self.job_id, "HANDLED_ERROR", str(exc)
            )

            return success(f"Successfully handled failed Job: {self.job_id}")

        else:
            try:
                self.process_sqs_messages(records)
                self.logger.write_log(
                    "UTI9995",
                    None,
                    {
                        "logger": "LR02.Lambda",
                        "level": "INFO",
                        "message": f"{num_of_records} messages processed successfully for Job: {self.job_id}",
                    },
                )

            except Exception as exc:
                self.handle_extract(RETRY_PREFIX)

                log_dynamodb_error(
                    self.log_object, self.logger, self.job_id, "HANDLED_ERROR", str(exc)
                )

                return success(f"Successfully handled failed Job: {self.job_id}")

            self.handle_extract(PASSED_PREFIX)

            return success(
                f"{upload_filename} processed successfully for Job: {self.job_id}"
            )

    def write_to_dynamodb(
        self,
        gp_ha_cipher: str,
        upload_filename: str,
        records: list,
        num_of_records: int,
    ) -> list:
        """Creates Job items and writes a batch of validated records to DynamoDb.
            Appends 'Id' field to each validated patient record in records dict

        Args:
            gp_ha_cipher (str): HA cypher of GP extract
            upload_filename (str): Filename of uploaded GP extract
            records (list): List of validated record dicts
            num_of_records (int): Number of validated records

        Returns:
            Records (list): List of Records with added ID field
        """

        job_item = Jobs(
            self.job_id,
            PracticeCode="tbc",
            FileName=upload_filename,
            Timestamp=get_datetime_now(),
            StatusId="1",
        )
        job_item.save()

        in_flight_item = InFlight(self.job_id, TotalRecords=num_of_records)
        in_flight_item.save()

        record_items = []
        for record in records:
            record_id = {"ID": str(uuid4())}
            record.update(record_id)

            record_items.append(
                Demographics(
                    Id=record["ID"],
                    JobId=self.job_id,
                    NhsNumber=empty_string(record["NHS_NUMBER"]),
                    IsComparisonCompleted=False,
                    GP_GpCode=str("tbc"),
                    GP_HaCipher=str(gp_ha_cipher),
                    GP_TransactionDate=str(
                        record["DATE_OF_DOWNLOAD"][:10].replace("-", "")
                    ),
                    GP_TransactionTime=str(
                        record["DATE_OF_DOWNLOAD"][11:16].replace(":", "")
                    ),
                    GP_TransactionId=str(record["TRANS_ID"]),
                    GP_Surname=empty_string(record["SURNAME"]),
                    GP_Forenames=empty_string(record["FORENAMES"]),
                    GP_PreviousSurname=empty_string(record["PREV_SURNAME"]),
                    GP_Title=empty_string(record["TITLE"]),
                    GP_Gender=empty_string(str(record["SEX"])),
                    GP_DateOfBirth=empty_string(record["DOB"].replace("-", "")),
                    GP_AddressLine1=empty_string(record["ADDRESS_LINE1"]),
                    GP_AddressLine2=empty_string(record["ADDRESS_LINE2"]),
                    GP_AddressLine3=empty_string(record["ADDRESS_LINE3"]),
                    GP_AddressLine4=empty_string(record["ADDRESS_LINE4"]),
                    GP_AddressLine5=empty_string(record["ADDRESS_LINE5"]),
                    GP_PostCode=empty_string(record["POSTCODE"]),
                    GP_DrugsDispensedMarker=empty_string(
                        record["DRUGS_DISPENSED_MARKER"]
                    ),
                )
            )

            with Demographics.batch_write() as batch:
                for item in record_items:
                    batch.save(item)

        self.logger.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR02.Lambda",
                "level": "INFO",
                "message": f"Job {self.job_id} created",
            },
        )

        return records

    def process_sqs_messages(self, records: list):
        """Add each record as a message using SQS. Asserts the number
            of messages added is equal to the number of validated records

        Args:
            records (Records): List of validated records
        """

        sqs_client = self.create_client("sqs")

        sqs_queue = sqs_client.get_queue_url(
            QueueName=self.lambda_env["AWS_PATIENT_RECORD_SQS"]
        )

        queue_url = sqs_queue["QueueUrl"]

        for record in records:
            msg = {
                "job_id": self.job_id,
                "patient_id": record["ID"],
                "nhs_number": record["NHS_NUMBER"],
            }

            response = self.send_message(sqs_client, queue_url, msg)

            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                raise SQSError("An error occurred when sending a record to SQS")

    @retry(
        stop_max_attempt_number=5,
        wait_exponential_multiplier=1000,
        wait_exponential_max=5000,
    )
    def send_message(self, sqs_client: BaseClient, url: str, msg: dict) -> dict:
        """Send a message to the SQS queue, with exponential retries

        Args:
            sqs_client (BaseClient): SQS client
            url (str): URL of SQS queue
            msg (dict): Message to send

        Returns:
            dict: response from SQS client.
        """

        return sqs_client.send_message(
            QueueUrl=url,
            MessageBody=json.dumps(msg),
            DelaySeconds=0,
            MessageGroupId=str(uuid4()),
        )

    def handle_extract(self, prefix: str, error_message: str = None):
        """Handles an GP extract file. Depending on validation status, will move file from:
            - inbound -> failed
            - inbound -> passed
            - inbound -> retry

        Args:
            prefix (str): S3 folder prefix for where to place the handled file
            error_message (str): message to handle.
        """

        s3_client = self.create_client("s3")

        bucket = self.lambda_env["AWS_S3_REGISTRATION_EXTRACT_BUCKET"]

        filename = self.upload_key.replace(INBOUND_PREFIX, "")
        key = prefix + filename

        s3_client.copy_object(
            Bucket=bucket,
            Key=key,
            CopySource={"Bucket": bucket, "Key": self.upload_key},
        )

        s3_client.delete_object(Bucket=bucket, Key=self.upload_key)

        if error_message:
            log_filename = filename + "_LOG.txt"
            log_key = FAILED_PREFIX + log_filename

            s3_client.put_object(Body=error_message, Bucket=bucket, Key=log_key)

    @staticmethod
    def process_invalid_message(exception: Exception) -> str:
        """Create a formatted error message string based on raised
            exception

        Args:
            exception (Exception): exception raised

        Returns:
            str: Error message as formatted string.
        """

        if isinstance(exception, AssertionError):
            msg = "DOW file content structure is invalid:\n" + str(exception)

        elif isinstance(exception, InvalidGPExtract):
            msg = "DOW file contains invalid records:\n"

            invalids = json.loads(str(exception))

            for i in invalids:
                msg += str(i) + "\n"

        else:
            msg = "DOW file is invalid:\n" + str(exception)

        return msg
