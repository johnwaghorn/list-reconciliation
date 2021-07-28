import json

import boto3
from spine_aws_common.lambda_application import LambdaApplication

from services.jobs import get_job
from utils import write_to_mem_csv, get_registration_filename, RegistrationType
from utils.database.models import Demographics, JobStats
from utils.logger import success, Success, log_dynamodb_error, UNHANDLED_ERROR
from utils.registration_status import GPRegistrationStatus


class GPRegistrations(LambdaApplication):
    def __init__(self):
        super().__init__()
        self.job_id = None

    def initialise(self):
        pass

    def start(self):
        try:
            self.job_id = str(self.event["job_id"])

            self.log_object.set_internal_id(self.job_id)

            self.response = json.dumps(self.get_gp_exclusive_registrations(self.job_id))

        except KeyError as err:
            error_message = f"Lambda event has missing {str(err)} key"
            self.response = {"message": error_message}
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR11.Lambda",
                    "level": "INFO",
                    "message": self.response["message"],
                },
            )

        except Exception as err:
            msg = f"Unhandled error getting gp registrations. JobId: {self.job_id or '99999999-0909-0909-0909-999999999999'}"
            error_response = log_dynamodb_error(self.log_object, self.job_id, UNHANDLED_ERROR, msg)

            raise Exception(error_response) from err

    def get_gp_exclusive_registrations(self, job_id: str) -> Success:
        """Create a GP-only registration differences file

        Args:
            job_id (str): Job ID.

        """
        practice_code = get_job(job_id).PracticeCode

        results = Demographics.JobIdIndex.query(
            job_id,
            filter_condition=Demographics.GP_RegistrationStatus
            != GPRegistrationStatus.MATCHED.value,
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
        boto3.client("s3").put_object(
            Body=stream.getvalue(),
            Bucket=self.system_config["LR_13_REGISTRATIONS_OUTPUT_BUCKET"],
            Key=key,
        )

        out = success(f"Got {len(rows)} GP-only registrations")
        out.update(filename=f"s3://{self.system_config['LR_13_REGISTRATIONS_OUTPUT_BUCKET']}/{key}")

        return out
