import json
import traceback

import boto3
import send_email
from aws.ssm import get_ssm_params
from lr_logging import error, get_cloudlogbase_config, success
from spine_aws_common.lambda_application import LambdaApplication


class SendEmail(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=get_cloudlogbase_config())
        self.s3 = boto3.client("s3")
        self.email_params = get_ssm_params(
            self.system_config["EMAIL_SSM_PREFIX"], self.system_config["AWS_REGION"]
        )

    def initialise(self):
        pass

    def start(self):
        try:
            bucket = self.event["Records"][0]["s3"]["bucket"]["name"]
            key = self.event["Records"][0]["s3"]["object"]["key"]
        except KeyError as e:
            self.response = error(
                "LR-send-emails Lambda tried to access missing key",
                self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e
        except Exception as e:
            self.response = error(
                "LR-send-emails Lambda unhandled exception caught",
                self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e

        email = self.generate_email(bucket, key)

        send_status = send_email.send(
            self.system_config["LISTREC_EMAIL"],
            self.email_params["list_rec_email_password"],
            email,
        )

        self.log_object.write_log(
            "LRSEI02",
            log_row_dict={
                "receiving_address": email["email_addresses"],
                "subject": email["subject"],
            },
        )

        if send_status is None:
            self.cleanup_files(bucket, key)
        else:
            self.response = error(
                message="lr_send_email email send failed",
                internal_id=self.log_object.internal_id,
                to=email["email_addresses"],
                email_subject=email["subject"],
            )

        self.response = success(
            message="lr_send_email email sent",
            internal_id=self.log_object.internal_id,
            to=email["email_addresses"],
            email_subject=email["subject"],
            email_body=email["message"],
            key=key,
        )

    def get_object(self, bucket, key):

        try:
            response = self.s3.get_object(Bucket=bucket, Key=key)

            self.log_object.write_log(
                "LRSEI01",
                log_row_dict={"key": key, "bucket": bucket},
            )
            return response
        except Exception as e:
            self.log_object.write_log(
                "LRSEC01",
                log_row_dict={"key": key, "bucket": bucket},
            )

            raise e

    def generate_email(self, bucket, key) -> dict:
        """Generates a dictionary from received s3 json

        Returns:
            to, subject, body (dict): email criteria
        """
        file = self.get_object(bucket, key)
        json_content = json.loads(file["Body"].read().decode("utf-8"))
        return {
            "email_addresses": json_content["to"],
            "subject": json_content["subject"],
            "message": json_content["body"],
        }

    def cleanup_files(self, bucket, key):
        """Cleanup already sent file from s3"""
        try:
            self.s3.delete_object(Bucket=bucket, Key=key)

            self.log_object.write_log(
                "LRSEI03",
                log_row_dict={"key": key, "bucket": bucket},
            )

        except Exception as e:
            self.log_object.write_log(
                "LRSEC02",
                log_row_dict={"key": key, "bucket": bucket},
            )

            raise e
