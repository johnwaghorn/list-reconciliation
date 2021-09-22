import json
from datetime import datetime, timedelta

import pytest
from database import InFlight, Jobs, JobStats
from jobs.statuses import JobStatus

from .conftest import JOB_ID


def test_lambda_handler_runs_successfully_no_errors_thrown(
    create_dynamo_tables, lambda_handler, lambda_context
):
    response = lambda_handler.main({}, lambda_context)

    assert response is not None
    assert response["status"] == "success"
    assert response["message"] == "LR09 Lambda application stopped"

    assert len(response["processed_jobs"]) == 0
    assert len(response["skipped_jobs"]) == 0
    assert len(response["timed_out_jobs"]) == 0


def test_empty_inflight_doesnt_process_jobs(create_dynamo_tables, lambda_handler):
    app = lambda_handler
    response = app.process_finished_jobs()

    assert response is not None
    assert response["status"] == "success"
    assert response["message"] == "LR09 Lambda application stopped"
    assert len(response["processed_jobs"]) == 0
    assert len(response["skipped_jobs"]) == 0


def test_four_inflight_records_one_processed_correctly_one_timed_out_two_skipped(
    create_dynamo_tables,
    populate_demographics_table,
    populate_inflight_table,
    populate_jobs_table,
    mock_step_function,
    lambda_handler,
):
    # Assert values are as expected before processing jobs
    with pytest.raises(StopIteration):
        before_job_stats = JobStats.query(JOB_ID[1])
        before_job_stats.next()

    before_validated_and_queued_job = Jobs.query(JOB_ID[1])
    assert (
        before_validated_and_queued_job.next().StatusId
        == JobStatus.VALIDATED_AND_QUEUED.value
    )

    before_timed_out_job = Jobs.query(JOB_ID[4])
    assert before_timed_out_job.next().StatusId == JobStatus.VALIDATED_AND_QUEUED.value

    # Act
    app = lambda_handler
    response = app.process_finished_jobs()

    assert response is not None
    assert response["status"] == "success"
    assert response["message"] == "LR09 Lambda application stopped"

    assert len(response["processed_jobs"]) == 1
    assert JOB_ID[1] in response["processed_jobs"]

    assert len(response["timed_out_jobs"]) == 1
    assert JOB_ID[4] in response["timed_out_jobs"]

    assert len(response["skipped_jobs"]) == 2
    assert JOB_ID[2] and JOB_ID[3] in response["skipped_jobs"]

    # Assert values are as expected after processing jobs
    with pytest.raises(StopIteration):
        deleted_in_flight_item = InFlight.query(JOB_ID[1])
        deleted_in_flight_item.next()

    after_job_stats = JobStats.query(JOB_ID[1])
    assert after_job_stats.next().TotalRecords == 6

    after_records_processed_job = Jobs.query(JOB_ID[1])
    assert (
        after_records_processed_job.next().StatusId == JobStatus.RECORDS_PROCESSED.value
    )

    after_timed_out_job = Jobs.query(JOB_ID[4])
    assert after_timed_out_job.next().StatusId == JobStatus.TIMED_OUT.value

    execution_history = mock_step_function[0].list_executions(
        stateMachineArn=mock_step_function[1]["stateMachineArn"]
    )["executions"]
    assert len(execution_history) > 0

    described_execution = mock_step_function[0].describe_execution(
        executionArn=execution_history[0]["executionArn"]
    )
    assert json.loads(described_execution["input"])["job_id"] == JOB_ID[1]
    assert described_execution["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_is_job_timed_out_timestamp_less_than_job_timeout_hours(lambda_handler):
    timestamp = datetime.now()
    job_timeout_hours = 1
    assert not lambda_handler.is_job_timed_out(timestamp, job_timeout_hours)


def test_is_job_timed_out_timestamp_more_than_job_timeout_hours(lambda_handler):
    timestamp = datetime.now() - timedelta(hours=2)
    job_timeout_hours = 1
    assert lambda_handler.is_job_timed_out(timestamp, job_timeout_hours)


def test_is_job_timed_out_timestamp_in_the_future(lambda_handler):
    timestamp = datetime.now() + timedelta(days=3)
    job_timeout_hours = 1
    assert not lambda_handler.is_job_timed_out(timestamp, job_timeout_hours)


def test_process_finished_jobs_no_inflight(lambda_handler, create_dynamo_tables):
    output = lambda_handler.process_finished_jobs()
    assert output["message"] == "LR09 Lambda application stopped"
