import boto3
import json
import os
import sys

from uuid import uuid4
from retrying import retry

from botocore.client import BaseClient
from pynamodb.exceptions import PynamoDBConnectionError, PutError
from spine_aws_common.lambda_application import LambdaApplication

from gp_file_parser.parser import parse_gp_extract_file_s3
from gp_file_parser.utils import empty_string

from utils.datetimezone import get_datetime_now
from utils.logger import log_dynamodb_error, success
from utils.exceptions import InvalidGPExtract, InvalidFilename, SQSError
from utils.database.models import Jobs, InFlight, Demographics

cwd = os.path.dirname(__file__)
ADDITIONAL_LOG_FILE = os.path.join(cwd, "..", "..", "utils/cloudlogbase.cfg")


class LR02LambdaHandler(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=ADDITIONAL_LOG_FILE)
        self.job_id = None
        self.upload_key = None
        self.upload_filename = None
        self.inbound_prefix = "inbound/"
        self.failed_prefix = "fail/"
        self.passed_prefix = "pass/"
        self.retry_prefix = "retry/"

    def initialise(self):
        self.job_id = str(uuid4())

    def start(self):
        try:
            self.upload_key = self.event["Records"][0]["s3"]["object"]["key"]
            self.upload_filename = self.upload_key.replace(self.inbound_prefix, "")

            self.response = self.validate_and_process_extract()

            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR02.Lambda",
                    "level": "INFO",
                    "message": self.response["message"],
                },
            )

        except KeyError as err:
            error_message = f"Lambda event has missing {str(err)} key"
            self.log_object.write_log(
                "UTI9998",
                sys.exc_info(),
                {
                    "logger": "LR02.Lambda",
                    "level": "ERROR",
                    "message": error_message,
                },
            )
            self.response = {"message": error_message}

        except Exception as err:
            self.log_object.write_log(
                "UTI9998",
                sys.exc_info(),
                {
                    "logger": "LR02.Lambda",
                    "level": "ERROR",
                    "message": str(err),
                },
            )
            self.response = {"message": str(err)}

    def validate_and_process_extract(self) -> success:
        """Handler to process and validate an uploaded S3 object containing a GP flat
            file extract

        Returns:
            success: A dict result containing a status and message
        """
        upload_date = get_datetime_now()

        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR02.Lambda",
                "level": "INFO",
                "message": f"{self.upload_key} validation process begun at {upload_date}",
            },
        )

        try:
            validated_file = parse_gp_extract_file_s3(
                self.system_config["AWS_S3_REGISTRATION_EXTRACT_BUCKET"],
                self.upload_key,
                upload_date,
            )

            return self.handle_validated_records(validated_file)

        except (AssertionError, InvalidGPExtract, InvalidFilename) as exc:
            message = self.process_invalid_message(exc)

            self.handle_extract(self.failed_prefix, message)

            msg = f"Handled error for invalid file upload: {self.upload_filename}"
            log_dynamodb_error(self.log_object, self.job_id, "HANDLED_ERROR", msg)

            return success(
                f"Invalid file {self.upload_filename} handled successfully for Job: {self.job_id}"
            )

    def handle_validated_records(self, validated_file: dict) -> success:
        """Handler to process validated patient records

        Args:
            validated_file (dict): dict of validated file, containing extract date, GP code,
                HA Cipher and a list of valid patient records

        Returns:
            success: A dict result containing a status and message
        """

        num_of_records = len(validated_file['records'])
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR02.Lambda",
                "level": "INFO",
                "message": f"{self.upload_filename} results collected: {num_of_records} records",
            },
        )

        try:
            records = self.write_to_dynamodb(validated_file, num_of_records)
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR02.Lambda",
                    "level": "INFO",
                    "message": f"Batch write to demographics was successful for Job: {self.job_id}",
                },
            )

        except (PynamoDBConnectionError, PutError) as exc:
            self.handle_extract(self.retry_prefix)

            log_dynamodb_error(
               self.log_object, self.job_id, "HANDLED_ERROR", str(exc)
            )

            return success(f"Successfully handled failed Job: {self.job_id}")

        else:
            try:
                self.process_sqs_messages(records)
                self.log_object.write_log(
                    "UTI9995",
                    None,
                    {
                        "logger": "LR02.Lambda",
                        "level": "INFO",
                        "message": f"{num_of_records} messages processed successfully for Job: {self.job_id}",
                    },
                )

            except SQSError as exc:
                self.handle_extract(self.retry_prefix)

                log_dynamodb_error(
                    self.log_object, self.job_id, "HANDLED_ERROR", str(exc)
                )

                return success(
                    f"Successfully handled failed Job: {self.job_id}"
                )

            self.handle_extract(self.passed_prefix)

            return success(
                f"{self.upload_filename} processed successfully for Job: {self.job_id}"
            )

    def write_to_dynamodb(self, validated_file: dict, num_of_records: int) -> list:
        """Creates Job items and writes a batch of validated records to DynamoDb.
            Appends 'Id' field to each validated patient record in records

        Args:
            validated_file (dict): dict of validated file, containing extract date, GP code,
                HA Cipher and a list of valid patient records
            num_of_records (int): Number of validated records

        Returns:
            Records (list): List of Records with added ID field
        """

        practice_code = validated_file["practice_code"]
        ha_cipher = validated_file["ha_cipher"]
        records = validated_file["records"]

        job_item = Jobs(
            self.job_id,
            PracticeCode=practice_code,
            FileName=self.upload_filename,
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
                    GP_GpCode=str(practice_code),
                    GP_HaCipher=str(ha_cipher),
                    GP_TransactionDate=str(record["DATE_OF_DOWNLOAD"][:10].replace("-", "")),
                    GP_TransactionTime=str(record["DATE_OF_DOWNLOAD"][11:16].replace(":", "")),
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
                    GP_DrugsDispensedMarker=empty_string(record["DRUGS_DISPENSED_MARKER"]),
                )
            )

        with Demographics.batch_write() as batch:
            for item in record_items:
                batch.save(item)

        self.log_object.write_log(
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

        sqs_client = boto3.client("sqs", region_name=self.system_config["AWS_REGION"])

        sqs_queue = sqs_client.get_queue_url(
            QueueName=self.system_config["AWS_PATIENT_RECORD_SQS"]
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

        s3_client = boto3.client("s3")

        bucket = self.system_config["AWS_S3_REGISTRATION_EXTRACT_BUCKET"]
        key = prefix + self.upload_filename

        s3_client.copy_object(
            Bucket=bucket,
            Key=key,
            CopySource={"Bucket": bucket, "Key": self.upload_key},
        )

        s3_client.delete_object(Bucket=bucket, Key=self.upload_key)

        if error_message:
            log_filename = self.upload_filename + "_LOG.txt"
            log_key = self.failed_prefix + log_filename

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
