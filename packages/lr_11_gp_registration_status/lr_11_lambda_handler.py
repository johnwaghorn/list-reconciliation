import traceback

import boto3
from database.models import Demographics, JobStats
from jobs.jobs import get_job
from lr_csv.csv import write_to_mem_csv
from lr_logging import get_cloudlogbase_config
from lr_logging.responses import Message, error, success
from pds_api.pds_api import SensitiveMarkers
from registration import (
    GPRegistrationStatus,
    RegistrationType,
    get_registration_filename,
)
from spine_aws_common.lambda_application import LambdaApplication


class GPRegistrations(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=get_cloudlogbase_config())
        self.s3 = boto3.client("s3")
        self.job_id = None
        self.bucket = None

    def initialise(self):
        pass

    def start(self):
        try:
            self.job_id = str(self.event["job_id"])
            self.bucket = self.system_config["LR_13_REGISTRATIONS_OUTPUT_BUCKET"]

            self.log_object.set_internal_id(self.job_id)

            self.response = self.get_gp_exclusive_registrations(self.job_id)

        except KeyError as e:
            self.response = error(
                f"LR11 Lambda tried to access missing key with error={traceback.format_exc()}",
                self.log_object.internal_id,
            )
            raise e

        except Exception as e:
            self.response = error(
                f"Unhandled exception caught in LR11 Lambda with error={traceback.format_exc()}",
                self.log_object.internal_id,
            )
            raise e

    def get_gp_exclusive_registrations(self, job_id: str) -> Message:
        """Create a GP-only registration differences file

        Args:
            job_id (str): Job ID.

        Returns:
            Message: A dict result containing a status and message
        """

        practice_code = get_job(job_id).PracticeCode

        results = Demographics.JobIdIndex.query(
            job_id,
            filter_condition=(
                Demographics.GP_RegistrationStatus != GPRegistrationStatus.MATCHED.value
            )
            & ~(
                Demographics.PDS_Sensitive.is_in(
                    SensitiveMarkers.RESTRICTED.value,
                    SensitiveMarkers.VERY_RESTRICTED.value,
                    SensitiveMarkers.REDACTED.value,
                )
            ),
        )

        rows = [
            {
                "SURNAME": result.GP_Surname,
                "FORENAMES": result.GP_Forenames,
                "DOB": result.GP_DateOfBirth,
                "NHS NO.": result.NhsNumber,
                "ADD 1": result.GP_AddressLine1,
                "ADD 2": result.GP_AddressLine2,
                "ADD 3": result.GP_AddressLine3,
                "ADD 4": result.GP_AddressLine4,
                "ADD 5": result.GP_AddressLine5,
                "POSTCODE": result.GP_PostCode,
                "TITLE": result.GP_Title,
                "SEX": result.GP_Gender,
                "STATUS": result.GP_RegistrationStatus,
                "STATUS DATE": result.PDS_GpRegisteredDate,
            }
            for result in results
        ]

        try:
            job_stat = JobStats.get(job_id)

        except JobStats.DoesNotExist:
            JobStats(job_id, OnlyOnGpRecords=len(rows)).save()

        else:
            job_stat.update(actions=[JobStats.OnlyOnGpRecords.set(len(rows))])

        self.log_object.write_log(
            "LR11I01",
            log_row_dict={
                "job_id": self.job_id,
            },
        )

        filename = get_registration_filename(practice_code, RegistrationType.GP)

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
            "STATUS",
            "STATUS DATE",
        ]
        stream = write_to_mem_csv(rows, header)

        key = f"{job_id}/{filename}"
        self.s3.put_object(
            Body=stream.getvalue(),
            Bucket=self.bucket,
            Key=key,
        )

        self.log_object.write_log(
            "LR11I02",
            log_row_dict={
                "file_name": filename,
                "record_count": len(rows),
                "bucket": self.bucket,
                "job_id": self.job_id,
            },
        )

        response = success(
            f"LR11 Lambda application stopped for jobId='{self.job_id}'",
            self.log_object.internal_id,
        )
        response.update(filename=f"s3://{self.bucket}/{key}")

        return response
