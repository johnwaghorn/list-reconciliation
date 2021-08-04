import json
from datetime import datetime, timedelta
from typing import Dict

import boto3
from spine_aws_common.lambda_application import LambdaApplication

from utils.database.models import Jobs, InFlight, Demographics, JobStats
from utils.logger import log_dynamodb_error
from utils.statuses import JobStatus


class ScheduledCheck(LambdaApplication):
    def __init__(self):
        super().__init__()
        self.job_timeout_hours = int(str(self.system_config["JOB_TIMEOUT_HOURS"]))

    def initialise(self):
        pass

    def start(self):
        try:
            self.log_object.set_internal_id(self._create_new_internal_id())
            self.response = self.process_finished_jobs()
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "Schedule check",
                    "level": "INFO",
                    "message": self.response["message"],
                },
            )

        except Exception as err:
            error_response = log_dynamodb_error(
                self.log_object,
                "99999999-0909-0909-0909-999999999999",
                "UNHANDLED_ERROR",
                "Unhandled error when running the scheduled check",
            )
            self.response = error_response
            raise type(err)(error_response) from err

    @staticmethod
    def is_job_complete(job_id: str, total_records: int) -> bool:
        response = Demographics.JobIdIndex.count(
            job_id, filter_condition=Demographics.IsComparisonCompleted == True
        )
        return response == total_records

    @staticmethod
    def is_job_timed_out(timestamp: datetime, job_timeout_hours: int) -> bool:
        cutoff_time = datetime.now() - timedelta(hours=job_timeout_hours)
        return timestamp.replace(tzinfo=None) < cutoff_time

    @staticmethod
    def update_job_stats(job_id: str, total_records: int) -> None:
        job_stats = JobStats(job_id, TotalRecords=total_records)
        job_stats.save()

    @staticmethod
    def update_job_status(job_id: str, status: str) -> None:
        job = Jobs.IdIndex.query(job_id)
        for j in job:
            j.StatusId = status
            j.save()

    def trigger_step_function(self, job_id: str) -> None:
        client = boto3.client("stepfunctions", region_name=self.system_config["AWS_REGION"])
        client.start_execution(
            stateMachineArn=self.system_config["LR_10_STEP_FUNCTION_ARN"],
            input=json.dumps({"job_id": job_id}),
        )

    def process_finished_jobs(self) -> Dict:
        """
        Scheduled checker to check the in flight jobs status.
        If they have finished, push them through to LR-10 (step function)
        If they have passed the cutoff time, delete the job and raise a log that can be alerted on
        """
        processed_jobs = []
        skipped_jobs = []
        timed_out_jobs = []

        in_flight = InFlight.scan()
        for item in in_flight:
            if self.is_job_complete(item.JobId, int(item.TotalRecords)):
                InFlight.delete(item)
                self.update_job_stats(item.JobId, int(item.TotalRecords))
                self.update_job_status(item.JobId, JobStatus.PDS_FHIR_API_PROCESSED.value)
                self.trigger_step_function(item.JobId)
                processed_jobs.append(item.JobId)
            elif self.is_job_timed_out(item.Timestamp, self.job_timeout_hours):
                InFlight.delete(item)
                self.log_object.write_log(
                    "UTI9995",
                    None,
                    {
                        "logger": "Schedule check",
                        "level": "CRITICAL",
                        "message": f"JobID: {item.JobId}, status: TIMED_OUT {JobStatus.TIMED_OUT.value}",
                    },
                )
                self.update_job_status(item.JobId, JobStatus.TIMED_OUT.value)
                timed_out_jobs.append(item.JobId)
            else:
                skipped_jobs.append(item.JobId)
                continue

        return {
            "status": "success",
            "message": "Scheduled checked successfully completed.",
            "processed_jobs": processed_jobs,
            "skipped_jobs": skipped_jobs,
            "timed_out_jobs": timed_out_jobs,
        }
