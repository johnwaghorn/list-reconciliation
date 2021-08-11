import csv
import io
import json
from datetime import datetime
from typing import Dict, List

import boto3
import botocore
from spine_aws_common.lambda_application import LambdaApplication

from services.jobs import get_job
from utils import write_to_mem_csv, get_registration_filename, RegistrationType
from utils.database.models import Demographics, JobStats
from utils.logger import log_dynamodb_error, success, UNHANDLED_ERROR
from utils.pds_api_service import PDSAPIHelper, PDSAPIError


class PDSRegistrationStatus(LambdaApplication):
    def __init__(self):
        super().__init__()
        self.api = PDSAPIHelper(self.system_config)
        self.job_id = None

    def initialise(self):
        pass

    def start(self):
        try:
            self.job_id = str(self.event["job_id"])

            self.log_object.set_internal_id(self.job_id)

            self.response = json.dumps(self.get_pds_exclusive_registrations(self.job_id))

        except KeyError as err:
            error_message = f"Lambda event has missing {str(err)} key"
            self.response = {"message": error_message}
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR12.Lambda",
                    "level": "INFO",
                    "message": self.response["message"],
                },
            )

        except Exception as err:
            msg = f"Unhandled error getting PDS registrations. JobId: {self.job_id or '99999999-0909-0909-0909-999999999999'}"
            error_response = log_dynamodb_error(self.log_object, self.job_id, UNHANDLED_ERROR, msg)
            self.response = error_response

            raise Exception(error_response) from err

    def get_practice_patients(self, practice_code: str) -> List[str]:
        """Get NHS numbers for patients registered at a practice from PDS extract.

        Args:
            practice_code (str): GP Practice code to get patient NHS numbers for.

        Returns:
            List[str]: List of NHS Numbers.
        """

        s3 = boto3.client("s3")
        key = f"{practice_code}.csv"
        bucket_path = f"{self.system_config['LR_22_PDS_PRACTICE_REGISTRATIONS_BUCKET']}/{key}"
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR12.Lambda",
                "level": "INFO",
                "message": f"Fetching {bucket_path}",
            },
        )

        try:
            obj = s3.get_object(
                Bucket=self.system_config["LR_22_PDS_PRACTICE_REGISTRATIONS_BUCKET"],
                Key=key,
            )
        except botocore.exceptions.ClientError:
            raise FileNotFoundError(f"File does not exist: {bucket_path}")

        contents = obj["Body"].read().decode()
        records = list(csv.DictReader(io.StringIO(contents)))

        return records

    def get_pds_exclusive_registrations(self, job_id: str) -> Dict[str, str]:
        """Create a PDS-only registration differences file

        Args:
            job_id (str): Job ID.

        """

        practice_code = get_job(job_id).PracticeCode
        practice_patients = self.get_practice_patients(practice_code)

        rows = []

        job_nhs_numbers = [r.NhsNumber for r in Demographics.JobIdIndex.query(job_id)]

        for patient in practice_patients:
            nhs_number = patient["nhs_number"]

            if nhs_number not in job_nhs_numbers:
                try:
                    pds_record = self.api.get_pds_record(nhs_number, job_id)

                except PDSAPIError as err:
                    msg = f"Error fetching PDS record for NHS number {nhs_number}, {err}"
                    error_response = log_dynamodb_error(self.log_object, job_id, err, msg)

                    raise PDSAPIError(json.dumps(error_response)) from err

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
                        "DATE ACCEPT.": datetime.strptime(
                            pds_record["gp_registered_date"], "%Y-%m-%d"
                        ).date(),
                    }
                )

        try:
            job_stat = JobStats.get(job_id)

        except JobStats.DoesNotExist:
            JobStats(job_id, OnlyOnPdsRecords=len(rows)).save()

        else:
            job_stat.update(actions=[JobStats.OnlyOnPdsRecords.set(len(rows))])

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

        key = f"{job_id}/{filename}"
        boto3.client("s3").put_object(
            Body=stream.getvalue(),
            Bucket=self.system_config["LR_13_REGISTRATIONS_OUTPUT_BUCKET"],
            Key=key,
        )

        out = success("Got PDS-only registrations")
        out.update(filename=f"s3://{self.system_config['LR_13_REGISTRATIONS_OUTPUT_BUCKET']}/{key}")

        return out
