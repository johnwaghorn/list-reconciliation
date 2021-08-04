import json
import sys
from uuid import uuid4

import boto3
from botocore.client import BaseClient
from pynamodb.exceptions import PynamoDBConnectionError, PutError
from spine_aws_common.lambda_application import LambdaApplication

from gp_file_parser.parser import parse_gp_extract_file_s3
from services.split_records_to_s3 import split_records_to_s3

from utils import InputFolderType
from utils.database.models import Jobs, InFlight
from utils.datetimezone import get_datetime_now
from utils.logger import log_dynamodb_error, success
from utils.exceptions import InvalidGPExtract, InvalidFilename, InvalidStructure

INVALID_RECORDS = "INVALID_RECORDS"
INVALID_STRUCTURE = "INVALID_STRUCTURE"
INVALID_FILENAME = "INVALID_FILENAME"


class ValidateAndParse(LambdaApplication):
    def __init__(self):
        super().__init__()
        self.job_id = None
        self.practice_code = None
        self.upload_key = None
        self.upload_filename = None
        self.upload_date = None

    def initialise(self):
        self.job_id = str(uuid4())

    def start(self):
        try:
            self.upload_key = self.event["Records"][0]["s3"]["object"]["key"]

            self.upload_filename = self.upload_key.replace(InputFolderType.IN.value, "")

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

            raise

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

            raise type(err)(str(err)) from err

    def create_client(self, service: str) -> BaseClient:
        return boto3.client(service, region_name=self.system_config["AWS_REGION"])

    def validate_and_process_extract(self) -> success:
        """Handler to process and validate an uploaded S3 object containing a GP flat
            file extract

        Returns:
            success: A dict result containing a status and message
        """

        self.upload_date = get_datetime_now()

        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR02.Lambda",
                "level": "INFO",
                "message": f"{self.upload_key} validation process begun at {self.upload_date}",
            },
        )

        try:
            validated_file = parse_gp_extract_file_s3(
                self.system_config["AWS_S3_REGISTRATION_EXTRACT_BUCKET"],
                self.upload_key,
                self.upload_date,
            )

            return self.handle_validated_records(validated_file)

        except (InvalidStructure, InvalidGPExtract, InvalidFilename) as exc:
            message = json.dumps(self.process_invalid_message(exc))

            self.handle_extract(InputFolderType.FAIL, message)

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

        num_of_records = len(validated_file["records"])
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
            self.write_to_dynamodb(validated_file["practice_code"], num_of_records)
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR02.Lambda",
                    "level": "INFO",
                    "message": f"Update job stats was successful for Job: {self.job_id}",
                },
            )

        except (PynamoDBConnectionError, PutError) as exc:
            self.handle_extract(InputFolderType.RETRY)

            log_dynamodb_error(self.log_object, self.job_id, "HANDLED_ERROR", str(exc))

            return success(f"Successfully handled failed Job: {self.job_id}")

        else:
            try:
                json_records = []
                for record in validated_file["records"]:
                    record.update(
                        practice_code=validated_file["practice_code"],
                        job_id=self.job_id,
                        id=str(uuid4()),
                    )
                    json_records.append(json.dumps(record))

                split_records_to_s3(
                    json_records,
                    ["job_id", "practice_code", "id"],
                    self.system_config["LR_06_BUCKET"],
                    "LR02.Lambda",
                )
                self.log_object.write_log(
                    "UTI9995",
                    None,
                    {
                        "logger": "LR02.Lambda",
                        "level": "INFO",
                        "message": f"{num_of_records} messages processed successfully for Job: {self.job_id}",
                    },
                )

            except Exception as exc:
                self.handle_extract(InputFolderType.RETRY)

                log_dynamodb_error(self.log_object, self.job_id, "HANDLED_ERROR", str(exc))

                return success(f"Successfully handled failed Job: {self.job_id}")

            self.handle_extract(InputFolderType.PASS)

            return success(f"{self.upload_filename} processed successfully for Job: {self.job_id}")

    def write_to_dynamodb(self, practice_code: str, num_of_records: int):
        """Creates Job items in DynamoDb.

        Args:
            practice_code (str): GP practice code of GP extract.
            num_of_records (int): Number of validated records.
        """

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

        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR02.Lambda",
                "level": "INFO",
                "message": f"Job {self.job_id} created",
            },
        )

    def handle_extract(self, prefix: InputFolderType, error_message: str = None):
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
        key = f"{prefix.value}{self.upload_filename}"

        s3_client.copy_object(
            Bucket=bucket,
            Key=key,
            CopySource={"Bucket": bucket, "Key": self.upload_key},
        )

        s3_client.delete_object(Bucket=bucket, Key=self.upload_key)

        if error_message:
            timestamp = self.upload_date.strftime("%Y%m%d%H%M%S")

            log_filename = f"{self.upload_filename}_FailedFile_{timestamp}.json"
            log_key = f"{InputFolderType.FAIL.value}logs/{log_filename}"

            s3_client.put_object(Body=error_message, Bucket=bucket, Key=log_key)

    def process_invalid_message(self, exception: Exception) -> str:
        """Create a formatted error message string based on raised
            exception

        Args:
            exception (Exception): exception raised

        Returns:
            dict: dictionary of failed file information
        """

        fail_log = {
            "file": self.upload_filename,
            "upload_date": str(self.upload_date),
        }

        if isinstance(exception, InvalidStructure):
            error = {"error_type": INVALID_STRUCTURE, "message": [exception.args[0]]}

        elif isinstance(exception, InvalidGPExtract):
            msg = exception.args[0]

            error = {
                "error_type": INVALID_RECORDS,
                "total_records": msg["total_records"],
                "total_invalid_records": len(msg["invalid_records"]),
                "message": msg["invalid_records"],
            }

        elif isinstance(exception, InvalidFilename):
            msg = exception.args[0]["message"]

            error = {"error_type": INVALID_FILENAME, "message": msg}

        fail_log.update(error)

        return fail_log
