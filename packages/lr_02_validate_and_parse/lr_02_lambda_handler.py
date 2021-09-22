import json
import traceback
from datetime import datetime
from uuid import uuid4

import boto3
from aws.split_records_to_s3 import split_records_to_s3
from database import InFlight, Jobs
from gp_file_parser.parser import parse_gp_extract_file_s3
from jobs.statuses import InputFolderType, InvalidErrorType
from lr_logging import get_cloudlogbase_config
from lr_logging.exceptions import InvalidFilename, InvalidGPExtract, InvalidStructure
from lr_logging.responses import Message, error, success
from pynamodb.exceptions import PutError, PynamoDBConnectionError
from spine_aws_common.lambda_application import LambdaApplication


class ValidateAndParse(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=get_cloudlogbase_config())
        self.job_id = None
        self.practice_code = None
        self.upload_key = None
        self.upload_filename = None
        self.upload_date = None

        self.s3 = boto3.client("s3")

    def initialise(self):
        pass

    def start(self):
        try:
            self.job_id = str(uuid4())
            self.upload_key = self.event["Records"][0]["s3"]["object"]["key"]
            self.upload_filename = self.upload_key.replace(InputFolderType.IN.value, "")
            self.log_object.set_internal_id(self.job_id)
            self.response = self.validate_and_process_extract()

        except KeyError as e:
            self.response = error(
                message="LR02 Lambda tried to access missing key",
                internal_id=self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e

        except Exception as e:
            self.response = error(
                message="LR02 Lambda unhandled exception caught",
                internal_id=self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e

    def validate_and_process_extract(self) -> Message:
        """Handler to process and validate an uploaded S3 object containing a GP flat
            file extract

        Returns:
            success: A dict result containing a status and message
        """

        self.upload_date = datetime.now()

        self.log_object.write_log(
            "LR02I01",
            log_row_dict={
                "upload_key": self.upload_key,
                "upload_date": self.upload_date,
                "job_id": self.job_id,
            },
        )

        try:
            validated_file = parse_gp_extract_file_s3(
                self.s3,
                self.system_config["AWS_S3_REGISTRATION_EXTRACT_BUCKET"],
                self.upload_key,
                self.upload_date,
            )

            self.upload_filename = validated_file["filename"]

            self.log_object.write_log(
                "LR02I05",
                log_row_dict={
                    "upload_filename": self.upload_filename,
                    "job_id": self.job_id,
                },
            )

            return self.handle_validated_records(validated_file)

        except (InvalidStructure, InvalidGPExtract, InvalidFilename) as exc:
            message = json.dumps(self.process_invalid_message(exc))

            self.handle_extract(InputFolderType.FAIL, message)

            self.log_object.write_log(
                "LR02I06",
                log_row_dict={
                    "upload_filename": self.upload_filename,
                    "job_id": self.job_id,
                },
            )

            return success(
                message="LR02 Lambda application stopped",
                internal_id=self.log_object.internal_id,
                job_id=self.job_id,
            )

    def handle_validated_records(self, validated_file: dict) -> Message:
        """Handler to process validated patient records

        Args:
            validated_file (dict): dict of validated file, containing extract date, GP code,
                HA Cipher and a list of valid patient records

        Returns:
            success: A dict result containing a status and message
        """

        num_of_records = len(validated_file["records"])

        self.log_object.write_log(
            "LR02I02",
            log_row_dict={
                "num_of_records": num_of_records,
                "upload_filename": self.upload_filename,
                "job_id": self.job_id,
            },
        )

        try:
            self.write_to_dynamodb(validated_file["practice_code"], num_of_records)

            self.log_object.write_log(
                "LR02I03",
                log_row_dict={
                    "upload_filename": self.upload_filename,
                    "job_id": self.job_id,
                },
            )

        except (PynamoDBConnectionError, PutError):
            self.handle_extract(InputFolderType.RETRY)

            self.log_object.write_log(
                "LR02C01",
                log_row_dict={"job_id": self.job_id},
            )

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
                    "LR02I04",
                    log_row_dict={
                        "num_of_records": num_of_records,
                        "job_id": self.job_id,
                    },
                )

            except Exception:
                self.handle_extract(InputFolderType.RETRY)

                self.log_object.write_log(
                    "LR02C02",
                    log_row_dict={
                        "num_of_records": num_of_records,
                        "job_id": self.job_id,
                    },
                )

            self.handle_extract(InputFolderType.PASS)

            return success(
                message="LR02 Lambda application stopped",
                internal_id=self.log_object.internal_id,
                job_id=self.job_id,
            )

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
            Timestamp=datetime.now(),
            StatusId="1",
        )
        job_item.save()

        in_flight_item = InFlight(self.job_id, TotalRecords=num_of_records)
        in_flight_item.save()

    def handle_extract(self, prefix: InputFolderType, error_message: str = None):
        """Handles an GP extract file. Depending on validation status, will move file from:
            - inbound -> failed
            - inbound -> passed
            - inbound -> retry

        Args:
            prefix (str): S3 folder prefix for where to place the handled file
            error_message (str): message to handle.
        """

        bucket = self.system_config["AWS_S3_REGISTRATION_EXTRACT_BUCKET"]
        key = f"{prefix.value}{self.upload_filename}"

        self.s3.copy_object(
            Bucket=bucket,
            Key=key,
            CopySource={"Bucket": bucket, "Key": self.upload_key},
        )

        self.s3.delete_object(Bucket=bucket, Key=self.upload_key)

        if error_message:
            log_filename = f"{self.upload_filename}-FailedFile-{self.job_id}.json"
            log_key = f"{InputFolderType.FAIL.value}logs/{log_filename}"

            self.s3.put_object(Body=error_message, Bucket=bucket, Key=log_key)

    def process_invalid_message(self, exception: Exception) -> str:
        """Create a formatted error message string based on raised
            exception

        Args:
            exception (Exception): exception raised

        Returns:
            dict: dictionary of failed file information
        """

        fail_log = {"file": self.upload_filename, "upload_date": str(self.upload_date)}

        if isinstance(exception, InvalidStructure):
            error = {
                "error_type": InvalidErrorType.STRUCTURE.value,
                "message": [exception.args[0]],
            }

        elif isinstance(exception, InvalidGPExtract):
            msg = exception.args[0]

            error = {
                "error_type": InvalidErrorType.RECORDS.value,
                "total_records": msg["total_records"],
                "total_invalid_records": len(msg["invalid_records"]),
                "message": msg["invalid_records"],
            }

        elif isinstance(exception, InvalidFilename):
            msg = exception.args[0]["message"]

            error = {"error_type": InvalidErrorType.FILENAME.value, "message": msg}

        fail_log.update(error)

        return fail_log
