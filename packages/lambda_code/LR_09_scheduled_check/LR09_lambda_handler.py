import json
from typing import Dict

import boto3
from spine_aws_common.lambda_application import LambdaApplication

from utils.logger import success, log_dynamodb_error
from utils.database.models import Jobs, InFlight, Demographics, JobStats
from utils.statuses import JobStatus
import os

cwd = os.path.dirname(__file__)
ADDITIONAL_LOG_FILE = os.path.join(cwd, "..", "..", "utils/cloudlogbase.cfg")


class ScheduledCheck(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=ADDITIONAL_LOG_FILE)

    def initialise(self):
        pass

    def start(self):
        try:
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
    def update_job_stats(job_id: str, total_records: int) -> None:
        job_stats = JobStats(job_id, TotalRecords=total_records)

        job_stats.save()

    @staticmethod
    def update_job_status_id(job_id: str) -> None:
        job = Jobs.IdIndex.query(job_id)

        for j in job:
            j.StatusId = JobStatus.PDS_FHIR_API_PROCESSED.value
            j.save()

    def trigger_step_function(self, job_id: str) -> None:
        client = boto3.client(
            "stepfunctions", region_name=self.system_config["AWS_REGION"]
        )

        client.start_execution(
            stateMachineArn=self.system_config["LR_10_STEP_FUNCTION_ARN"],
            input=json.dumps({"job_id": job_id}),
        )

    def process_finished_jobs(self) -> Dict:
        """
        Scheduled checker to check the in flight jobs, validate if they've finished,
        and if they have, push them through to LR-10 (step function)
        """

        processed_jobs = []
        skipped_jobs = []

        in_flight = InFlight.scan()

        for item in in_flight:
            is_complete = self.is_job_complete(item.JobId, int(item.TotalRecords))

            if not is_complete:
                skipped_jobs.append(item.JobId)
                continue

            InFlight.delete(item)

            self.update_job_stats(item.JobId, item.TotalRecords)

            self.update_job_status_id(item.JobId)

            self.trigger_step_function(item.JobId)

            processed_jobs.append(item.JobId)

        response: dict = success("Scheduled checked successfully completed.")
        response.update(processed_jobs=processed_jobs, skipped_jobs=skipped_jobs)
        return response
