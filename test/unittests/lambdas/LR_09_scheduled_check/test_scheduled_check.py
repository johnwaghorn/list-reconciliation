import json
import pytest

from lambdas.LR_09_scheduled_check.scheduled_check import process_finished_jobs
from utils.models import InFlight, Jobs, JobStats
from utils.statuses import JobStatus

JOB_ID = "b204b5f4-6762-414e-bb6b-a05c37f52956"
JOB_ID_2 = "3af674be-1e7f-470c-b6d1-ca5ce6d9c600"
JOB_ID_3 = "87e36ab6-4f25-4c47-9e13-d029f1e4c925"


def test_empty_inflight_doesnt_process_jobs(create_dynamo_tables):
    response = process_finished_jobs()

    assert response is not None
    assert response["status"] == "success"
    assert response["message"] == "Scheduled checked successfully completed."
    assert len(response["processed_jobs"]) == 0
    assert len(response["skipped_jobs"]) == 0


def test_three_inflight_records_one_processed_correctly_two_skipped(
        create_dynamo_tables,
        populate_demographics_table,
        populate_inflight_table,
        populate_jobs_table,
        mock_step_function
):
    # Assert values are as expected before processing jobs
    with pytest.raises(StopIteration):
        before_job_stats = JobStats.query(JOB_ID)
        before_job_stats.next()

    before_job = Jobs.query(JOB_ID)
    assert before_job.next().StatusId == JobStatus.ADDED_TO_QUEUE.value

    # Act
    response = process_finished_jobs()

    assert response is not None
    assert response["status"] == "success"
    assert response["message"] == "Scheduled checked successfully completed."

    assert len(response["processed_jobs"]) == 1
    assert JOB_ID in response["processed_jobs"]

    assert len(response["skipped_jobs"]) == 2
    assert JOB_ID_2 and JOB_ID_3 in response["skipped_jobs"]

    # Assert values are as expected after processing jobs
    with pytest.raises(StopIteration):
        deleted_in_flight_item = InFlight.query(JOB_ID)
        deleted_in_flight_item.next()

    after_job_stats = JobStats.query(JOB_ID)
    assert after_job_stats.next().TotalRecords == 6

    after_job = Jobs.query(JOB_ID)
    assert after_job.next().StatusId == JobStatus.PDS_FHIR_API_PROCESSED.value

    execution_history = mock_step_function[0].list_executions(stateMachineArn=mock_step_function[1]["stateMachineArn"])["executions"]
    assert len(execution_history) > 0
    described_execution = mock_step_function[0].describe_execution(executionArn=execution_history[0]["executionArn"])

    assert json.loads(described_execution["input"])["job_id"] == JOB_ID
    assert described_execution["ResponseMetadata"]["HTTPStatusCode"] == 200