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
from utils.logger import success, error, Message

cwd = os.path.dirname(__file__)
ADDITIONAL_LOG_FILE = os.path.join(cwd, "..", "..", "utils/cloudlogbase.cfg")


class SplitDPSExtract(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=ADDITIONAL_LOG_FILE)
        self.s3 = boto3.client("s3")
        self.input_bucket = self.system_config["LR_20_SUPPLEMENTARY_INPUT_BUCKET"]
        self.output_bucket = self.system_config["LR_22_SUPPLEMENTARY_OUTPUT_BUCKET"]
        self.upload_key = None

    def start(self):
        try:
            self.upload_key = self.event["Records"][0]["s3"]["object"]["key"]

            self.response = self.split_dps_extract()

        except InvalidDSAFile:
            self.response = error(
                f'LR21 Lambda processed an invalid DSA file in uploadPath="{self.upload_key}"',
                self.log_object.internal_id,
            )

        except KeyError as err:
            self.response = error(
                f"LR21 Lambda tried to access missing key={str(err)}", self.log_object.internal_id
            )

        except Exception:
            self.response = error(
                f"Unhandled exception caught in LR21 Lambda", self.log_object.internal_id
            )

    def split_dps_extract(self) -> Message:
        """Splits a DPS supplementary file into multiple smaller files by practice

        Returns:
            Message: A dict result containing a status and message
        """

        records = self.read_file()

        per_registered_gp = self.split_file(records)

        self.write_files(per_registered_gp)

        self.cleanup_files()

        return success("LR21 Lambda application stopped", self.log_object.internal_id)

    def read_file(self) -> list:
        """Retrieve and read supplementary file data

        Returns:
            list: A list of strings containing file data
        """

        try:
            file_obj = self.s3.get_object(Bucket=self.input_bucket, Key=self.upload_key)

            file_data = file_obj["Body"].read().decode("utf-8").splitlines()

            headers = ["NHS Number,Registered GP Practice,Dispensing Flag"]

            if not file_data or file_data == headers:
                raise InvalidDSAFile("File is empty")

        except (ClientError, UnicodeDecodeError) as err:
            self.log_object.write_log(
                "LR21C01",
                log_row_dict={
                    "file_name": self.upload_key,
                    "bucket": self.input_bucket,
                },
            )

            raise InvalidDSAFile(f"Failed to read supplementary data from file") from err

        else:
            return file_data

    def split_file(self, file_data: list) -> dict:
        """Split file data into a dict for each registered GP

        Args:
            file_data (list): A list of strings containing file data

        Returns:
            dict: A dict of registered GP's
        """

        try:
            per_registered_gp = defaultdict(list)

            reader = csv.reader(file_data)

            next(reader, None)

            for nhs_number, gp_practicecode, disp_flag in reader:
                per_registered_gp[gp_practicecode.strip()].append(
                    {
                        "nhs_number": nhs_number.strip(),
                        "dispensing_flag": int(disp_flag),
                    }
                )

            return dict(per_registered_gp)

        except ValueError as err:
            self.log_object.write_log(
                "LR21C02",
                log_row_dict={
                    "file_name": self.upload_key,
                    "bucket": self.input_bucket,
                },
            )

            raise InvalidDSAFile(f"Failed to process supplementary data from file") from err

    def write_files(self, per_registered_gp: dict):
        """Create and write each GP dict it's own GP file

        Args:
            per_registered_gp (dict): A dict of registered GP's
        """

        headers = ["nhs_number", "dispensing_flag"]

        for gp, patients in per_registered_gp.items():
            stream = io.StringIO()

            writer = csv.DictWriter(stream, fieldnames=headers, lineterminator="\n")
            writer.writeheader()
            writer.writerows(patients)

            csv_results_string = stream.getvalue().strip()

            try:
                self.s3.put_object(
                    Body=csv_results_string, Bucket=self.output_bucket, Key=f"{gp}.csv"
                )

            except ClientError as err:
                self.log_object.write_log(
                    "LR21C03",
                    log_row_dict={
                        "file_name": self.upload_key,
                        "bucket": self.input_bucket,
                    },
                )

        self.log_object.write_log(
            "LR21I01",
            log_row_dict={
                "practice_count": len(per_registered_gp),
                "bucket": self.input_bucket,
            },
        )

    def cleanup_files(self):
        """Cleanup any file from the LR-22 output bucket, which hasn't been recently modified and remove the DSA
        upload file from LR-20 input bucket"""

        try:
            minimum_last_update = get_datetime_now() - timedelta(hours=4)

            paginator = self.s3.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.output_bucket)

            for page in pages:
                for obj in page.get("Contents", []):
                    mod_date = localize_date(obj["LastModified"])

                    if mod_date < minimum_last_update:
                        self.s3.delete_object(Bucket=self.output_bucket, Key=obj["Key"])

                        self.log_object.write_log(
                            "LR21I02",
                            log_row_dict={
                                "file_name": obj["Key"],
                                "bucket": self.input_bucket,
                            },
                        )

            self.s3.delete_object(Bucket=self.input_bucket, Key=self.upload_key)

            self.log_object.write_log(
                "LR21I03",
                log_row_dict={
                    "file_name": self.upload_key,
                    "bucket": self.input_bucket,
                },
            )

        except Exception:
            self.log_object.write_log(
                "LR21C04",
                log_row_dict={
                    "bucket": self.input_bucket,
                },
            )
