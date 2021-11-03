import json
import traceback
import uuid
from datetime import datetime
from uuid import UUID

import boto3
from botocore.exceptions import ClientError
from jobs.statuses import InputFolderType, InvalidErrorType
from lr_logging import get_cloudlogbase_config
from lr_logging.exceptions import FeedbackLogError, SendEmailError
from lr_logging.responses import Message, error, success
from send_email.send import to_outbox
from spine_aws_common.lambda_application import LambdaApplication


class FeedbackFailure(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=get_cloudlogbase_config())
        self.s3 = boto3.client("s3")
        self.bucket = self.system_config["AWS_S3_REGISTRATION_EXTRACT_BUCKET"]
        self.outbox_bucket = self.system_config["AWS_S3_SEND_EMAIL_BUCKET"]
        self.to = self.system_config["PCSE_EMAIL"]
        self.job_id = None
        self.log_key = None
        self.log_filename = None
        self.failed_key = None
        self.log = None
        self.upload_date = None
        self.prefix = f"{InputFolderType.FAIL.value}logs/"

    def initialise(self):
        pass

    def start(self):
        try:

            self.log_key = self.event["Records"][0]["s3"]["object"]["key"]
            self.log_filename = str(self.log_key).replace(self.prefix, "")

            try:
                self.job_id = self.log_filename.split("-FailedFile-")[1].replace(
                    ".json", ""
                )

                # Check job_id string is a valid UUID
                UUID(str(self.job_id))

                self.log_object.set_internal_id(self.job_id)

            except (IndexError, ValueError):
                raise FeedbackLogError("LOG filename is missing valid Job Id")

            self.response = self.process_failed_upload_file()

        except FeedbackLogError as e:
            self.log_object.write_log(
                "LR04C01",
                log_row_dict={
                    "log_key": self.log_key,
                    "error": traceback.format_exc(),
                    "job_id": self.job_id,
                },
            )
            self.response = error(
                message="LR04 Lambda accessed invalid log file",
                internal_id=self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e

        except SendEmailError as e:
            self.log_object.write_log(
                "LR04C02",
                log_row_dict={
                    "email_address": self.to,
                    "upload_filename": self.log["file"],
                    "job_id": self.job_id,
                    "error": traceback.format_exc(),
                },
            )
            self.response = error(
                message="LR04 Lambda failed to Send_Email",
                internal_id=self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e

        except KeyError as e:
            self.response = error(
                message="LR04 Lambda tried to access missing key",
                internal_id=self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e

        except Exception as e:
            self.response = error(
                message="LR04 Lambda unhandled exception caught",
                internal_id=self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e

    def process_failed_upload_file(self) -> Message:
        """Reads LOG data and process the failed GP extract file, sends email containing invalid reasons,
            and cleans bucket

        Returns:
            Message: A dict result containing a status and message
        """

        self.read_log()

        self.validate_log()

        email_subject, email_body, sent = self.send_email()

        self.cleanup_files()

        if sent:
            return success(
                message="LR04 Lambda application stopped",
                internal_id=self.log_object.internal_id,
                job_id=self.job_id,
                email_subject=email_subject,
                email_body=email_body,
            )
        else:
            return error(
                message="lr-04 failed to send alert email",
                internal_id=self.log_object.internal_id,
                job_id=self.job_id,
                email_subject=email_subject,
                email_body=email_body,
            )

    def read_log(self):
        """Read LOG file and extract error information into a dictionary"""

        try:
            log_obj = self.s3.get_object(Bucket=self.bucket, Key=self.log_key)

            log_data = log_obj["Body"].read().decode("utf-8")
            log = json.loads(log_data)

        except (UnicodeDecodeError, ValueError):
            msg = "LOG file contains invalid data. Could not read file contents"
            raise FeedbackLogError(msg)

        self.log = log

    def validate_log(self):
        """Validates LOG dictionary's structure and data values. If successful, set the `failed_key`

        Raises:
            FeedbackLogError: If validation fails
        """

        try:
            self.upload_date = datetime.strptime(
                self.log["upload_date"], "%Y-%m-%d %H:%M:%S.%f%z"
            )
            self.failed_key = f"{InputFolderType.FAIL.value}{self.log['file']}"

            try:
                self.s3.get_object(Bucket=self.bucket, Key=self.failed_key)

            except ClientError:
                raise FeedbackLogError(
                    f"LOG file contains reference to failed file='{self.failed_key}' that could not be found"
                )

            error_types = [
                InvalidErrorType.RECORDS.value,
                InvalidErrorType.STRUCTURE.value,
                InvalidErrorType.FILENAME.value,
            ]
            error_type = self.log["error_type"]

            if error_type not in error_types:
                raise FeedbackLogError("LOG file contains an invalid error type")

            if error_type == InvalidErrorType.RECORDS.value:
                total_records = self.log["total_records"]
                if not isinstance(total_records, int) and not total_records > 0:
                    raise FeedbackLogError("LOG file contains unusable record total")

                total_invalid_records = self.log["total_invalid_records"]
                if (
                    not isinstance(total_invalid_records, int)
                    and not total_invalid_records > 0
                ):
                    raise FeedbackLogError(
                        "LOG file contains unusable invalid record total"
                    )

            if not self.log["message"]:
                raise FeedbackLogError("LOG file contains invalid error message")

            self.log_object.write_log(
                "LR04I01",
                log_row_dict={"log_key": self.log_key, "job_id": self.job_id},
            )

        except (ValueError, KeyError):
            msg = "LOG file contains invalid data. Could not read file contents"
            raise FeedbackLogError(msg)

    def send_email(self):
        """Send an email based on LOG file info"""

        service = "LR-04"
        to = self.to
        subject = f"Validation Failure - PDS Comparison validation failure against '{self.log['file']}'"
        body = self.create_email_body()
        outbox_filename = str(uuid.uuid4())
        bucket = self.outbox_bucket

        try:
            sent = to_outbox(service, [to], subject, body, outbox_filename, bucket)
            self.log_object.write_log(
                "LR04I02",
                log_row_dict={
                    "email_address": self.to,
                    "upload_filename": self.log["file"],
                    "job_id": self.job_id,
                    "outbox_filename": outbox_filename,
                },
            )
            return subject, body, sent
        except:

            raise SendEmailError(
                f"Failed to send email with subject='{subject}' to='{to} for '{self.job_id}'"
            )

    def create_email_body(self) -> str:
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

        if error_type == InvalidErrorType.RECORDS.value:
            body = self.create_invalid_records_body(body, log_message)

        else:
            body += "The reasons for the failure are:\n"
            message = "    •" + "\n    • ".join(log_message)
            body += message

        footer = "\nPlease check and amend the file content and upload again.\n"

        body += footer

        return body

    def create_invalid_records_body(self, body: str, records: dict) -> str:
        """Append email body with formatted invalid records

        Args:
            body (str): Formatted body of email
            records (dict): Dictionary of invalid records

        Returns:
            body (str): Formatted body of email appended with records
        """

        invalid_records_msg = ""

        for record in records:
            invalid_reasons = record["_INVALID_"]
            line_number = invalid_reasons["ON_LINES"]

            del record["_INVALID_"]["ON_LINES"]

            invalid_records_msg += f"Invalid Record on lines {line_number}\n"
            invalid_records_msg += "\n".join(
                [f"   • {record['_INVALID_'][r]}" for r in record["_INVALID_"]]
            )
            invalid_records_msg += "\n"

        body += (
            f"Total records: {self.log['total_records']}\n"
            f"Total invalid records: {self.log['total_invalid_records']}\n"
            f"\nThe reasons for the failure are:\n{invalid_records_msg}"
        )

        return body

    def cleanup_files(self):

        self.s3.delete_object(Bucket=self.bucket, Key=self.failed_key)

        self.log_object.write_log(
            "LR04I03",
            log_row_dict={"upload_filename": self.log["file"], "job_id": self.job_id},
        )
