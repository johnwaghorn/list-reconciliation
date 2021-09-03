import traceback

import boto3
from database.models import InFlight, Jobs
from jobs.statuses import JobStatus
from lr_logging.responses import Message, error, success
from spine_aws_common.lambda_application import LambdaApplication


class JobCleanup(LambdaApplication):
    def __init__(self):
        super().__init__()
        self.registrations_output_bucket = str(
            self.system_config["LR_13_REGISTRATIONS_OUTPUT_BUCKET"]
        )
        self.job_id = None

    def start(self):
        try:
            self.log_object.set_internal_id(self._create_new_internal_id())

            # pyright: reportOptionalSubscript=false
            self.job_id = self.event["job_id"]

            self.log_object.set_internal_id(self.job_id)

            self.response = self.process_job_cleanup()

        except KeyError as e:
            self.response = error(
                "LR27 Lambda tried to access missing key",
                self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e
        except Exception as e:
            self.response = error(
                "LR27 Lambda unhandled exception caught",
                self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e

    def process_job_cleanup(self) -> Message:
        job_exists = self.validate_job_id()
        if not job_exists:
            self.log_object.write_log(
                "LR27I01",
                log_row_dict={"job_id": self.job_id},
            )

            return success(
                message="LR27 Lambda application stopped",
                internal_id=self.log_object.internal_id,
                job_id=self.job_id,
            )

        self.log_object.write_log(
            "LR27I02",
            log_row_dict={"job_id": self.job_id},
        )

        self.maybe_delete_from_registrations_output_bucket()

        self.maybe_delete_from_inflight_table()

        self.update_job_status()

        self.log_object.write_log(
            "LR27I06",
            log_row_dict={"job_id": self.job_id},
        )

        return success(
            message="LR27 Lambda application stopped",
            internal_id=self.log_object.internal_id,
            job_id=self.job_id,
        )

    def validate_job_id(self) -> bool:
        jobs = Jobs.count(self.job_id)
        if jobs == 1:
            return True
        return False

    def maybe_delete_from_registrations_output_bucket(self) -> None:
        s3 = boto3.client("s3")
        objects = s3.list_objects_v2(
            Bucket=self.registrations_output_bucket, Prefix=self.job_id
        )
        for object in objects.get("Contents", []):
            key = object["Key"]
            object = s3.delete_object(Bucket=self.registrations_output_bucket, Key=key)

            self.log_object.write_log(
                "LR27I03",
                log_row_dict={
                    "file_name": key,
                    "bucket": self.registrations_output_bucket,
                    "job_id": self.job_id,
                },
            )

    def maybe_delete_from_inflight_table(self) -> None:
        try:
            job = InFlight.get(self.job_id)
            job.delete()

            self.log_object.write_log(
                "LR27I04",
                log_row_dict={
                    "inflight_table": InFlight.Meta.table_name,
                    "job_id": self.job_id,
                },
            )

        except InFlight.DoesNotExist:
            self.log_object.write_log(
                "LR27C01",
                log_row_dict={
                    "inflight_table": InFlight.Meta.table_name,
                    "job_id": self.job_id,
                },
            )

    def update_job_status(self) -> None:
        try:
            jobs = Jobs.query(self.job_id)
            for job in jobs:
                job.StatusId = JobStatus.CLEANED_UP.value
                job.save()

                self.log_object.write_log(
                    "LR27I05",
                    log_row_dict={"job_id": self.job_id},
                )

        except Jobs.DoesNotExist:
            self.log_object.write_log(
                "LR27C02",
                log_row_dict={"job_id": self.job_id},
            )
