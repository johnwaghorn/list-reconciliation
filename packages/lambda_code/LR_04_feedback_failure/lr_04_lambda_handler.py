import json
import sys
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from spine_aws_common.lambda_application import LambdaApplication

from lambda_code.LR_02_validate_and_parse.lr_02_lambda_handler import (
    INVALID_FILENAME,
    INVALID_RECORDS,
    INVALID_STRUCTURE,
)
from utils import InputFolderType
from utils.exceptions import FeedbackLogError
from utils.logger import log_dynamodb_error, success


class FeedbackFailure(LambdaApplication):
    def __init__(self):
        super().__init__()
        self.bucket = self.system_config["AWS_S3_REGISTRATION_EXTRACT_BUCKET"]
        self.log_key = None
        self.log_filename = None
        self.failed_key = None
        self.log = None
        self.upload_date = None

    def initialise(self):
        pass

    def start(self):
        try:
            self.log_key = self.event["Records"][0]["s3"]["object"]["key"]

            prefix = f"{InputFolderType.FAIL.value}logs/"

            self.log_filename = str(self.log_key).replace(prefix, "")

            self.response = self.process_failed_file()

            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR04.Lambda",
                    "level": "INFO",
                    "message": self.response["message"],
                },
            )

        except FeedbackLogError as err:
            error_message = f"LR-04 processed an invalid log file: {self.log_key}"
            self.log_object.write_log(
                "UTI9998",
                sys.exc_info(),
                {
                    "logger": "LR04.Lambda",
                    "level": "ERROR",
                    "message": str(err),
                },
            )
            self.response = {"message": error_message}

            raise

        except KeyError as err:
            error_message = f"Lambda event has missing {str(err)} key"
            self.log_object.write_log(
                "UTI9998",
                sys.exc_info(),
                {
                    "logger": "LR04.Lambda",
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
                    "logger": "LR04.Lambda",
                    "level": "ERROR",
                    "message": str(err),
                },
            )
            self.response = {"message": str(err)}

            raise type(err)(str(err)) from err

    def process_failed_file(self) -> success:
        """Reads LOG data and process the failed GP extract file, sends email containing invalid reasons,
            and cleans bucket

        Returns:
            success: A dict result containing a status and message
        """

        self.read_log()
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR04.Lambda",
                "level": "INFO",
                "message": "LR-04 successfully read log file",
            },
        )

        self.validate_log()
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR04.Lambda",
                "level": "INFO",
                "message": "LR-04 successfully validated log file",
            },
        )

        self.send_email()
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR04.Lambda",
                "level": "INFO",
                "message": "LR-04 successfully sent email",
            },
        )

        self.cleanup_files()
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR04.Lambda",
                "level": "INFO",
                "message": "LR-04 successfully cleaned up S3 files",
            },
        )

        return success(
            f"Invalid file={self.failed_key} handled successfully from log={self.log_filename}"
        )

    def read_log(self):
        """Read LOG file and extract error information into a dictionary"""

        try:
            client = boto3.client("s3")

            log_obj = client.get_object(Bucket=self.bucket, Key=self.log_key)

            log_data = log_obj["Body"].read().decode("utf-8")

            log = json.loads(log_data)

        except (UnicodeDecodeError, ValueError) as err:
            msg = f"Invalid log data detected in: {self.log_key}"
            error_response = log_dynamodb_error(
                self.log_object,
                "99999999-04-0404-0404-999999999999",
                "HANDLED_ERROR",
                msg,
            )

            raise FeedbackLogError(error_response) from err

        self.log = log

    def validate_log(self):
        """Validates LOG dictionary's structure and data values. If successful, set the `failed_key`

        Raises:
            FeedbackLogError: If validation fails
        """

        client = boto3.client("s3")

        try:
            failed_file_date = datetime.strptime(self.log["upload_date"], "%Y-%m-%d %H:%M:%S.%f%z")
            self.upload_date = failed_file_date

            self.failed_key = f"{InputFolderType.FAIL.value}{self.log['file']}"

            try:
                client.get_object(Bucket=self.bucket, Key=self.failed_key)

            except ClientError as err:
                raise FeedbackLogError(
                    "LOG contains reference to failed file that could not be found"
                )

            error_types = [INVALID_RECORDS, INVALID_STRUCTURE, INVALID_FILENAME]
            error_type = self.log["error_type"]

            if error_type not in error_types:
                raise FeedbackLogError("LOG contains invalid error type")

            if error_type == INVALID_RECORDS:
                total_records = self.log["total_records"]
                if not isinstance(total_records, int) and not total_records > 0:
                    raise FeedbackLogError("LOG contains unusable record total")

                total_invalid_records = self.log["total_invalid_records"]
                if not isinstance(total_invalid_records, int) and not total_invalid_records > 0:
                    raise FeedbackLogError("LOG contains unusable invalid record total")

            if not self.log["message"]:
                raise FeedbackLogError("LOG contains invalid message")

        except (ValueError, KeyError, FeedbackLogError) as err:
            msg = f"Log file: {self.log_key} does not contain the required data or format"
            error_response = log_dynamodb_error(
                self.log_object,
                "99999999-04-0404-0404-999999999999",
                "HANDLED_ERROR",
                msg,
            )

            raise FeedbackLogError(error_response) from err

    def send_email(self):
        """Send an email based on LOG info"""

        to = "test@nhs.net"
        subject = (
            f"Validation Failure - PDS Comparison validation failure against '{self.log['file']}'"
        )
        body = self.create_body()

        output = f"To: {to}\nSubject: {subject}\n{body}"

        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR04.Lambda",
                "level": "INFO",
                "message": output,
            },
        )

    def create_body(self) -> str:
        """Create body of email using LOG's error type and log data

        Returns:
            body (str): formatted body of email
        """

        date_string = self.upload_date.strftime("%H:%M:%S on %d/%m/%Y")

        header = (
            f"The GP file: {self.log['file']} failed validation at {date_string}.\n"
            "As a result, no records in this file have been processed.\n\n"
        )

        body = header

        error_type = self.log["error_type"]
        log_message = self.log["message"]

        if error_type == INVALID_RECORDS:
            records = log_message

            invalid_records_msg = ""

            for record in records:
                invalid_reasons = record["_INVALID_"]
                line_number = invalid_reasons["ON_LINES"]

                del record["_INVALID_"]["ON_LINES"]

                invalid_records_msg += f"Invalid Record on lines {line_number}\n"
                invalid_records_msg += (
                    "\n".join([f"- {record['_INVALID_'][r]}" for r in record["_INVALID_"]]) + "\n"
                )

            body += (
                f"Total records: {self.log['total_records']}\n"
                f"Total invalid records: {self.log['total_invalid_records']}\n"
                f"\nThe reasons for the failure are:\n{invalid_records_msg}"
            )

        else:
            body += "The reasons for the failure are:\n"
            message = "- " + "\n- ".join(log_message)
            body += message

        footer = "\nPlease check and amend the file content and upload again.\n"

        body += footer

        return body

    def cleanup_files(self):
        """Cleanup failed GP file and failed log file from s3"""

        client = boto3.client("s3")

        try:
            client.delete_object(Bucket=self.bucket, Key=self.failed_key)

        except ClientError as err:
            msg = f"LR-04 failed to remove failed upload file: {self.failed_key}"
            error_response = log_dynamodb_error(
                self.log_object,
                "99999999-04-0404-0404-999999999999",
                "HANDLED_ERROR",
                msg,
            )

            raise Exception(error_response) from err
