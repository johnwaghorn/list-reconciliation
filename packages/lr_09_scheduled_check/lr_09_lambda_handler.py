import json
import traceback
from datetime import datetime, timedelta

import boto3
import pytz
from database.models import Demographics, InFlight, Jobs, JobStats
from jobs.statuses import JobStatus
from lr_logging import Message, error, get_cloudlogbase_config, success
from spine_aws_common.lambda_application import LambdaApplication


class ScheduledCheck(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=get_cloudlogbase_config())
        self.job_timeout_hours = int(str(self.system_config["JOB_TIMEOUT_HOURS"]))

    def start(self):
        try:
            self.log_object.set_internal_id(self._create_new_internal_id())
            self.response = self.process_finished_jobs()
        except KeyError as e:
            self.response = error(
                f"LR09 Lambda tried to access missing key with error={traceback.format_exc()}",
                self.log_object.internal_id,
            )
            raise e
        except Exception as e:
            self.response = error(
                f"Unhandled exception caught in LR09 Lambda error='{traceback.format_exc()}",
                self.log_object.internal_id,
            )
            raise e

    @staticmethod
    def is_job_complete(job_id: str, total_records: int) -> bool:
        response = Demographics.JobIdIndex.count(
            job_id, filter_condition=Demographics.IsComparisonCompleted == True
        )
        return response == total_records

    @staticmethod
    def is_job_timed_out(timestamp: datetime, job_timeout_hours: int) -> bool:
        cutoff_time = datetime.now(tz=pytz.timezone("UTC")) - timedelta(
            hours=job_timeout_hours
        )
        return timestamp.astimezone(pytz.timezone("UTC")) < cutoff_time

    def update_job_stats(self, job_id: str, total_records: int) -> None:
        job_stats = JobStats(job_id, TotalRecords=total_records)
        job_stats.save()
        self.log_object.write_log("LR09I02", log_row_dict={"job_id": job_id})

    def update_job_status(self, job_id: str, status: str) -> None:
        job = Jobs.IdIndex.query(job_id)
        for j in job:
            j.StatusId = status
            j.save()
        self.log_object.write_log("LR09I03", log_row_dict={"job_id": job_id})

    def trigger_step_function(self, job_id: str) -> None:
        client = boto3.client(
            "stepfunctions", region_name=self.system_config["AWS_REGION"]
        )
        client.start_execution(
            stateMachineArn=self.system_config["LR_10_STEP_FUNCTION_ARN"],
            input=json.dumps({"job_id": job_id}),
        )
        self.log_object.write_log("LR09I04", log_row_dict={"job_id": job_id})

    def process_finished_jobs(self) -> Message:
        """
        Scheduled checker to check the in flight jobs status.
        If they have finished, push them through to LR-10 (step function)
        If they have passed the cutoff time, delete the in flight job item and raise a log that can be alerted on

        Returns:
            Message: A result containing a status and message
        """
        processed_jobs = []
        skipped_jobs = []
        timed_out_jobs = []

        in_flight = InFlight.scan()
        if in_flight.total_count == 0:
            self.log_object.write_log("LR09I05")

        for item in in_flight:
            if self.is_job_complete(item.JobId, int(item.TotalRecords)):
                InFlight.delete(item)
                self.update_job_stats(item.JobId, int(item.TotalRecords))
                self.update_job_status(item.JobId, JobStatus.RECORDS_PROCESSED.value)
                self.trigger_step_function(item.JobId)
                processed_jobs.append(item.JobId)
            elif self.is_job_timed_out(item.Timestamp, self.job_timeout_hours):
                InFlight.delete(item)
                self.log_object.write_log(
                    "LR09I06", log_row_dict={"job_id": item.JobId}
                )
                self.update_job_status(item.JobId, JobStatus.TIMED_OUT.value)
                timed_out_jobs.append(item.JobId)
            else:
                skipped_jobs.append(item.JobId)
                self.log_object.write_log(
                    "LR09I01", log_row_dict={"job_id": item.JobId}
                )
                continue

        response: dict = success(
            "LR09 Lambda application stopped", self.log_object.internal_id
        )
        response.update(
            processed_jobs=processed_jobs,
            skipped_jobs=skipped_jobs,
            timed_out_jobs=timed_out_jobs,
        )

        return response
