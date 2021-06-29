import os
import json
import boto3

from typing import Dict

from utils.logger import success, LOG, log_dynamodb_error
from utils.database.models import Jobs, InFlight, Demographics, JobStats
from utils.statuses import JobStatus

LR_10_STEP_FUNCTION_ARN = os.getenv("LR_10_STEP_FUNCTION_ARN")
AWS_REGION = os.getenv("AWS_REGION")


def is_job_complete(job_id: str, total_records: int) -> bool:
    response = Demographics.JobIdIndex.count(
        job_id,
        filter_condition=Demographics.IsComparisonCompleted == True
    )

    return response == total_records


def update_job_stats(job_id: str, total_records: int) -> None:
    job_stats = JobStats(
        job_id,
        TotalRecords=total_records
    )

    job_stats.save()


def update_job_status_id(job_id: str) -> None:
    job = Jobs.IdIndex.query(job_id).next()

    job.update(
        actions=[Jobs.StatusId.set(JobStatus.PDS_FHIR_API_PROCESSED.value)]
    )


def trigger_step_function(job_id: str) -> None:
    client = boto3.client("stepfunctions", region_name=AWS_REGION)

    client.start_execution(
        stateMachineArn=LR_10_STEP_FUNCTION_ARN,
        input=json.dumps({"job_id": job_id})
    )


def process_finished_jobs() -> Dict:
    """
    Scheduled checker to check the in flight jobs, validate if they've finished,
        and if they have, push them through to LR-10 (step function)
    """

    processed_jobs = []
    skipped_jobs = []

    in_flight = InFlight.scan()

    for item in in_flight:
        is_complete = is_job_complete(item.JobId, int(item.TotalRecords))

        if not is_complete:
            skipped_jobs.append(item.JobId)
            continue

        InFlight.delete(item)

        update_job_stats(item.JobId, item.TotalRecords)

        update_job_status_id(item.JobId)

        trigger_step_function(item.JobId)

        processed_jobs.append(item.JobId)

    response = success("Scheduled checked successfully completed.")
    response.update(
        processed_jobs=processed_jobs,
        skipped_jobs=skipped_jobs
    )

    return response


def lambda_handler(event, context):
    try:
        response = process_finished_jobs()
        LOG.info(response)

        return response

    except Exception as err:
        error_response = log_dynamodb_error(
            "99999999-0909-0909-0909-999999999999",
            "UNHANDLED_ERROR",
            "Unhandled error when running the scheduled check"
        )

        raise type(err)(error_response) from err
