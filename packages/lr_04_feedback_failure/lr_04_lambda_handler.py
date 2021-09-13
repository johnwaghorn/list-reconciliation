import json
import traceback
from datetime import datetime
from uuid import UUID

import boto3
import nhs_mail_relay
from aws.ssm import get_ssm_params
from botocore.exceptions import ClientError
from jobs.statuses import InputFolderType, InvalidErrorType
from lr_logging import get_cloudlogbase_config
from lr_logging.exceptions import FeedbackLogError
from lr_logging.responses import Message, error, success
from spine_aws_common.lambda_application import LambdaApplication


class FeedbackFailure(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=get_cloudlogbase_config())
        self.s3 = boto3.client("s3")
        self.bucket = self.system_config["AWS_S3_REGISTRATION_EXTRACT_BUCKET"]
        self.email_params = get_ssm_params(
            self.system_config["EMAIL_SSM_PREFIX"], self.system_config["AWS_REGION"]
        )
        self.job_id = None
        self.log_key = None
        self.log_filename = None
        self.failed_key = None
        self.log = None
        self.upload_date = None

    def initialise(self):
        pass

    def start(self):
        try:
            prefix = f"{InputFolderType.FAIL.value}logs/"

            self.log_key = self.event["Records"][0]["s3"]["object"]["key"]
            self.log_filename = str(self.log_key).replace(prefix, "")

            try:
                self.job_id = self.log_filename.split("-FailedFile-")[1].replace(".json", "")

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
                f"LR04 Lambda accessed invalid log file with error={traceback.format_exc()}",
                self.log_object.internal_id,
            )
            raise e

        except KeyError as e:
            self.response = error(
                f"LR04 Lambda tried to access missing key with error={traceback.format_exc()}",
                self.log_object.internal_id,
            )
            raise e

        except Exception as e:
            self.response = error(
                f"Unhandled exception caught in LR04 Lambda with error='{traceback.format_exc()}'",
                self.log_object.internal_id,
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

        email_subject, email_body = self.send_email()

        self.cleanup_files()

        output = success(
            f"LR04 Lambda application stopped for jobId='{self.job_id}'",
            self.log_object.internal_id,
        )

        output.update(email_subject=email_subject, email_body=email_body)

        return output

    def read_log(self):
        """Read LOG file and extract error information into a dictionary"""

        try:
            log_obj = self.s3.get_object(Bucket=self.bucket, Key=self.log_key)

            log_data = log_obj["Body"].read().decode("utf-8")
            log = json.loads(log_data)

        except (UnicodeDecodeError, ValueError):
            msg = f"LOG file contains invalid data. Could not read file contents"
            raise FeedbackLogError(msg)

        self.log = log

    def validate_log(self):
        """Validates LOG dictionary's structure and data values. If successful, set the `failed_key`

        Raises:
            FeedbackLogError: If validation fails
        """

        try:
            self.upload_date = datetime.strptime(self.log["upload_date"], "%Y-%m-%d %H:%M:%S.%f%z")
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
                if not isinstance(total_invalid_records, int) and not total_invalid_records > 0:
                    raise FeedbackLogError("LOG file contains unusable invalid record total")

            if not self.log["message"]:
                raise FeedbackLogError("LOG file contains invalid error message")

            self.log_object.write_log(
                "LR04I01",
                log_row_dict={"log_key": self.log_key, "job_id": self.job_id},
            )

        except (ValueError, KeyError):
            msg = f"LOG file contains invalid data. Could not read file contents"
            raise FeedbackLogError(msg)

    def send_email(self):
        """Send an email based on LOG file info"""

        to = self.system_config["PCSE_EMAIL"]
        subject = (
            f"Validation Failure - PDS Comparison validation failure against '{self.log['file']}'"
        )
        body = self.create_email_body()

        nhs_mail_relay.send_email(
            self.system_config["LISTREC_EMAIL"],
            self.email_params["list_rec_email_password"],
            {
                "email_addresses": [to],
                "subject": subject,
                "message": body,
            },
            self.log_object,
        )

        self.log_object.write_log(
            "LR04I02",
            log_row_dict={
                "email_address": self.log_key,
                "upload_filename": self.log["file"],
                "job_id": self.job_id,
            },
        )

        return subject, body

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
            invalid_records_msg += (
                "\n".join([f"   • {record['_INVALID_'][r]}" for r in record["_INVALID_"]]) + "\n"
            )

        body += (
            f"Total records: {self.log['total_records']}\n"
            f"Total invalid records: {self.log['total_invalid_records']}\n"
            f"\nThe reasons for the failure are:\n{invalid_records_msg}"
        )

        return body

    def cleanup_files(self):
        """Cleanup failed GP file and failed log file from s3"""

        self.s3.delete_object(Bucket=self.bucket, Key=self.failed_key)

        self.log_object.write_log(
            "LR04I03",
            log_row_dict={"upload_filename": self.log["file"], "job_id": self.job_id},
        )
