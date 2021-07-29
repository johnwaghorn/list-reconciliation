import json
import os

import boto3
from botocore.retries import bucket
from spine_aws_common.lambda_application import LambdaApplication

from utils.database.models import Jobs, InFlight
from utils.statuses import JobStatus


class JobCleanup(LambdaApplication):
    def __init__(self):
        super().__init__()
        self.registrations_output_bucket = str(
            self.system_config["LR_13_REGISTRATIONS_OUTPUT_BUCKET"]
        )

    def start(self):
        self.log_object.set_internal_id(self._create_new_internal_id())

        # pyright: reportOptionalSubscript=false
        job_id = self.event["job_id"]

        job_exists = self.validate_job_id(job_id)
        if not job_exists:
            msg = f"job_cleanup status=invalid job_id={job_id}"
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR27.Lambda",
                    "level": "INFO",
                    "message": msg,
                },
            )
            self.response = json.dumps({"msg": msg})
            return

        msg = f"job_cleanup status=started job_id={job_id}"
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR27.Lambda",
                "level": "INFO",
                "message": msg,
            },
        )
        self.response = json.dumps({"msg": msg})

        self.maybe_delete_from_registrations_output_bucket(job_id)

        self.maybe_delete_from_inflight_table(job_id)

        self.update_job_status(job_id)

        msg = f"job_cleanup status=complete job_id={job_id}"
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR27.Lambda",
                "level": "INFO",
                "message": msg,
            },
        )
        self.response = json.dumps({"msg": msg})
        return

    def validate_job_id(self, job_id: str) -> bool:
        jobs = Jobs.count(job_id)
        if jobs == 1:
            return True
        return False

    def maybe_delete_from_registrations_output_bucket(self, job_id: str) -> None:
        s3 = boto3.client("s3")
        objects = s3.list_objects_v2(Bucket=self.registrations_output_bucket, Prefix=job_id)
        for object in objects.get("Contents", []):
            key = object["Key"]
            object = s3.delete_object(Bucket=self.registrations_output_bucket, Key=key)
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR27.Lambda",
                    "level": "INFO",
                    "message": f"s3 object deleted bucket={self.registrations_output_bucket} key={key}",
                },
            )

    def maybe_delete_from_inflight_table(self, job_id: str) -> None:
        try:
            job = InFlight.get(job_id)
            job.delete()
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR27.Lambda",
                    "level": "INFO",
                    "message": f"deleted dynamodb record table={InFlight.Meta.table_name} key={job_id}",
                },
            )
        except InFlight.DoesNotExist:
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR27.Lambda",
                    "level": "INFO",
                    "message": f"no dynamodb record to delete table={InFlight.Meta.table_name} key={job_id}",
                },
            )

    def update_job_status(self, job_id: str) -> None:
        try:
            jobs = Jobs.query(job_id)
            for job in jobs:
                job.StatusId = JobStatus.CLEANED_UP.value
                job.save()
                self.log_object.write_log(
                    "UTI9995",
                    None,
                    {
                        "logger": "LR27.Lambda",
                        "level": "INFO",
                        "message": f"deleted dynamodb record table={Jobs.Meta.table_name} key={job_id}",
                    },
                )
        except Jobs.DoesNotExist:
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR27.Lambda",
                    "level": "INFO",
                    "message": f"no dynamodb record to delete table={Jobs.Meta.table_name} key={job_id}",
                },
            )
