import csv
import io
import traceback
from datetime import datetime

import boto3
import botocore
from database.models import Demographics, JobStats
from jobs.jobs import get_job
from lr_csv.csv import write_to_mem_csv
from lr_logging import Message, error, get_cloudlogbase_config, success
from pds_api.pds_api import PDSAPI, PDSAPIError, SensitiveMarkers
from registration import RegistrationType, get_registration_filename
from spine_aws_common.lambda_application import LambdaApplication


class PDSRegistrationStatus(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=get_cloudlogbase_config())
        self.s3 = boto3.client("s3")
        self.api = PDSAPI(self.system_config)
        self.lr13_bucket = self.system_config["LR_13_REGISTRATIONS_OUTPUT_BUCKET"]
        self.lr22_bucket = self.system_config["LR_22_PDS_PRACTICE_REGISTRATIONS_BUCKET"]
        self.job_id = None

    def initialise(self):
        pass

    def start(self):
        try:
            self.job_id = str(self.event["job_id"])

            self.log_object.set_internal_id(self.job_id)

            self.response = self.get_pds_exclusive_registrations()

        except KeyError as e:
            self.response = error(
                f"LR12 Lambda tried to access missing key with error={traceback.format_exc()}",
                self.log_object.internal_id,
            )
            raise e

        except Exception as e:
            self.response = error(
                f"Unhandled exception caught in LR12 Lambda with error={traceback.format_exc()}",
                self.log_object.internal_id,
            )
            raise e

    def get_practice_patients(self, practice_code: str) -> list[str]:
        """Get NHS numbers for patients registered at a practice from PDS extract.

        Args:
            practice_code (str): GP Practice code to get patient NHS numbers for.

        Returns:
            List[str]: List of NHS Numbers.
        """

        key = f"{practice_code}.csv"
        bucket_path = f"{self.lr22_bucket}/{key}"

        try:
            obj = self.s3.get_object(
                Bucket=self.lr22_bucket,
                Key=key,
            )

        except botocore.exceptions.ClientError:
            self.log_object.write_log(
                "LR12C01",
                log_row_dict={
                    "file_name": key,
                    "bucket_name": self.lr22_bucket,
                    "practice_code": practice_code,
                    "job_id": self.job_id,
                },
            )

            raise FileNotFoundError(f"File does not exist: {bucket_path}")

        contents = obj["Body"].read().decode()
        records = list(csv.DictReader(io.StringIO(contents)))

        return records

    def get_pds_exclusive_registrations(self) -> Message:
        """Create a PDS-only registration differences file

        Returns:
            Message: A result containing a status and message
        """

        practice_code = get_job(self.job_id).PracticeCode
        practice_patients = self.get_practice_patients(practice_code)

        self.log_object.write_log(
            "LR12I01",
            log_row_dict={
                "practice_code": practice_code,
                "bucket": self.lr22_bucket,
                "job_id": self.job_id,
            },
        )

        rows = []

        job_nhs_numbers = [
            r.NhsNumber for r in Demographics.JobIdIndex.query(self.job_id)
        ]

        for patient in practice_patients:
            nhs_number = patient["nhs_number"]

            if nhs_number not in job_nhs_numbers:
                try:
                    pds_record = self.api.get_pds_record(nhs_number, self.job_id)
                    if pds_record and any(
                        marker.value == pds_record.get("sensitive")
                        for marker in SensitiveMarkers
                    ):
                        self.log_object.write_log(
                            "LR12I02",
                            log_row_dict={
                                "nhs_number": nhs_number,
                                "job_id": self.job_id,
                            },
                        )
                        continue

                except PDSAPIError:
                    self.log_object.write_log(
                        "LR12C02",
                        log_row_dict={
                            "nhs_number": nhs_number,
                            "job_id": self.job_id,
                            "response_message": traceback.format_exc(),
                        },
                    )

                if pds_record:
                    pds_record["address"].extend([None, None, None, None, None])
                    date_accept = (
                        datetime.strptime(
                            pds_record["gp_registered_date"], "%Y-%m-%d"
                        ).date()
                        if pds_record["gp_registered_date"]
                        else ""
                    )
                    rows.append(
                        {
                            "SURNAME": pds_record["surname"],
                            "FORENAMES": " ".join(pds_record["forenames"]),
                            "DOB": pds_record["date_of_birth"],
                            "NHS NO.": nhs_number,
                            "ADD 1": pds_record["address"][0],
                            "ADD 2": pds_record["address"][1],
                            "ADD 3": pds_record["address"][2],
                            "ADD 4": pds_record["address"][3],
                            "ADD 5": pds_record["address"][4],
                            "POSTCODE": pds_record["postcode"],
                            "TITLE": ", ".join(pds_record["title"]),
                            "SEX": pds_record["gender"],
                            "DATE ACCEPT.": date_accept,
                        }
                    )

        try:
            job_stat = JobStats.get(self.job_id)

        except JobStats.DoesNotExist:
            JobStats(self.job_id, OnlyOnPdsRecords=len(rows)).save()

        else:
            job_stat.update(actions=[JobStats.OnlyOnPdsRecords.set(len(rows))])

        self.log_object.write_log(
            "LR12I03",
            log_row_dict={
                "job_id": self.job_id,
            },
        )

        filename = get_registration_filename(practice_code, RegistrationType.PDS)

        header = [
            "SURNAME",
            "FORENAMES",
            "DOB",
            "NHS NO.",
            "ADD 1",
            "ADD 2",
            "ADD 3",
            "ADD 4",
            "ADD 5",
            "POSTCODE",
            "TITLE",
            "SEX",
            "DATE ACCEPT.",
        ]
        stream = write_to_mem_csv(rows, header)

        key = f"{self.job_id}/{filename}"
        self.s3.put_object(
            Body=stream.getvalue(),
            Bucket=self.lr13_bucket,
            Key=key,
        )

        self.log_object.write_log(
            "LR12I04",
            log_row_dict={
                "file_name": filename,
                "record_count": len(rows),
                "bucket": self.lr13_bucket,
                "job_id": self.job_id,
            },
        )

        response = success(
            f"LR12 Lambda application stopped for jobId='{self.job_id}'",
            self.log_object.internal_id,
        )
        response.update(filename=f"s3://{self.lr13_bucket}/{key}")

        return response
