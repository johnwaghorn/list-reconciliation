import csv
import io
import os
from collections import defaultdict
from datetime import timedelta

import boto3
from botocore.exceptions import ClientError
from spine_aws_common.lambda_application import LambdaApplication

from utils.datetimezone import get_datetime_now, localize_date
from utils.exceptions import InvalidDSAFile
from utils.logger import log_dynamodb_error, success, UNHANDLED_ERROR

cwd = os.path.dirname(__file__)
ADDITIONAL_LOG_FILE = os.path.join(cwd, "..", "..", "utils/cloudlogbase.cfg")


class SplitDPSExtract(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=ADDITIONAL_LOG_FILE)
        self.input_bucket = self.system_config["LR_20_SUPPLEMENTARY_INPUT_BUCKET"]
        self.output_bucket = self.system_config["LR_22_SUPPLEMENTARY_OUTPUT_BUCKET"]

    def start(self):
        try:
            upload_key = self.event["Records"][0]["s3"]["object"]["key"]

            self.response = self.split_dps_extract(upload_key)

        except Exception as err:
            msg = f"Unhandled error when processing supplementary data file in LR-21"
            error_response = log_dynamodb_error(
                self.log_object,
                "99999999-2121-2121-2121-999999999999",
                UNHANDLED_ERROR,
                msg,
            )
            self.response = {"message": msg}

            raise Exception(error_response) from err

    def split_dps_extract(self, upload_key: str) -> success:
        """Splits a DPS supplementary file into multiple smaller files by practice

        Args:
            upload_key (str): A path to the s3 file key object

        Returns:
            success: A dict result containing a status and message
        """

        records = self.read_file(upload_key)
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR02.Lambda",
                "level": "INFO",
                "message": "Data lines extracted",
            },
        )

        per_registered_gp = self.split_file(upload_key, records)
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR02.Lambda",
                "level": "INFO",
                "message": "Dictionary created for each registered GP",
            },
        )

        self.write_files(per_registered_gp)
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR21.Lambda",
                "level": "INFO",
                "message": "Output files for each registered GP was successful",
            },
        )

        self.cleanup_files(upload_key, per_registered_gp)
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR21.Lambda",
                "level": "INFO",
                "message": "Outdated GP file cleanup was successful",
            },
        )

        return success(
            f"LR-21 processed Supplementary data successfully, from file: {upload_key}"
        )

    def read_file(self, upload_key: str) -> list:
        """Retrieve and read supplementary file data

        Args:
            upload_key (str): A path to the s3 file key object

        Returns:
            list: A list of strings containing file data
        """

        try:
            client = boto3.client("s3")

            file_obj = client.get_object(Bucket=self.input_bucket, Key=upload_key)

            file_data = file_obj["Body"].read().decode("utf-8").splitlines()

            return file_data

        except (ClientError, UnicodeDecodeError) as err:
            msg = f"LR-21 failed to read supplementary data from: {upload_key}"
            error_response = log_dynamodb_error(
                self.log_object,
                "99999999-2121-2121-2121-999999999999",
                "HANDLED_ERROR",
                msg,
            )

            raise InvalidDSAFile(error_response) from err

    def split_file(self, upload_key: str, file_data: list) -> dict:
        """Split file data into a dict for each registered GP

        Args:
            upload_key (str): A path to the s3 file key object
            file_data (list): A list of strings containing file data

        Returns:
            dict: A dict of registered GP's
        """

        try:
            per_registered_gp = defaultdict(list)

            reader = csv.reader(file_data)

            next(reader, None)

            for nhs_number, gp_code, disp_flag in reader:
                per_registered_gp[gp_code.strip()].append(
                    {
                        "nhs_number": nhs_number.strip(),
                        "dispensing_flag": int(disp_flag),
                    }
                )

            return dict(per_registered_gp)

        except ValueError as err:
            msg = f"LR-21 failed to process file contents for: {upload_key}"
            error_response = log_dynamodb_error(
                self.log_object,
                "99999999-2121-2121-2121-999999999999",
                "HANDLED_ERROR",
                msg,
            )

            raise InvalidDSAFile(error_response) from err

    def write_files(self, per_registered_gp: dict):
        """Create and write each GP dict it's own GP file

        Args:
            per_registered_gp (dict): A dict of registered GP's
        """

        client = boto3.client("s3")

        headers = ["nhs_number", "dispensing_flag"]

        for gp, patients in per_registered_gp.items():
            stream = io.StringIO()

            writer = csv.DictWriter(stream, fieldnames=headers, lineterminator="\n")
            writer.writeheader()
            writer.writerows(patients)

            csv_results_string = stream.getvalue().strip()

            try:
                client.put_object(
                    Body=csv_results_string, Bucket=self.output_bucket, Key=f"{gp}.csv"
                )

            except ClientError as err:
                msg = f"Failed to write processed data to output bucket in LR-21"

                error_response = log_dynamodb_error(
                    self.log_object,
                    self.log_object,
                    "99999999-2121-2121-2121-999999999999",
                    "HANDLED_ERROR",
                    msg,
                )

                raise Exception(error_response) from err

    def cleanup_files(self, upload_key: str, per_registered_gp: dict):
        """Cleanup outdated GP files and clean input bucket

        Args:
            upload_key (str): A path to the s3 file key object
            per_registered_gp (dict): A dict of registered GP's
        """

        client = boto3.client("s3")

        try:
            minimum_last_update = get_datetime_now() - timedelta(hours=4)

            paginator = client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.output_bucket)

            for page in pages:
                for obj in page["Contents"]:
                    mod_date = localize_date(obj["LastModified"])

                    if mod_date < minimum_last_update:
                        client.delete_object(Bucket=self.output_bucket, Key=obj["Key"])
                        self.log_object.write_log(
                            "UTI9995",
                            None,
                            {
                                "logger": "LR21.Lambda",
                                "level": "INFO",
                                "message": f"Outdated GP data deleted for GP:{str(obj['Key']).replace('.csv', '')}",
                            },
                        )

            client.delete_object(Bucket=self.input_bucket, Key=upload_key)

        except ClientError as err:
            msg = f"Failed to cleanup files in output bucket in LR-21"
            error_response = log_dynamodb_error(
                self.log_object,
                "99999999-2121-2121-2121-999999999999",
                "HANDLED_ERROR",
                msg,
            )

            raise Exception(error_response) from err
