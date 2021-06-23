import pytest
import datetime

from moto import mock_dynamodb2

from utils.logger import log_dynamodb_error, log_dynamodb_status, success
from utils.models import Errors, Jobs
from utils.datetimezone import localize_date


@pytest.fixture
def create_dynamodb_tables():
    with mock_dynamodb2():
        Errors.create_table()
        Jobs.create_table()
        yield


@pytest.fixture
def job_record(create_dynamodb_tables):
    obj = Jobs(
        "1",
        PracticeCode="ABC",
        FileName="test.csv",
        StatusId="1",
        Timestamp=localize_date(datetime.datetime(2021, 5, 27)),
    )
    obj.save()
    yield


def test_log_dynamodb_error_logs_error(create_dynamodb_tables):
    log_dynamodb_error("123", "TEST", "TEST MESSAGE")

    error = [e for e in Errors.scan()][0]

    assert error.JobId == "123"
    assert error.Name == "TEST"
    assert error.Description == "TEST MESSAGE"


def test_log_dynamodb_error_logs_error_with_no_job_id(create_dynamodb_tables):
    log_dynamodb_error("", "TEST", "TEST MESSAGE")

    error = [e for e in Errors.scan()][0]

    assert error.JobId == "99999999-0909-0909-0909-999999999999"
    assert error.Name == "TEST"
    assert error.Description == "TEST MESSAGE"


def test_log_dynamodb_error_unexpected_fail_logs_error():
    with pytest.raises(Exception):
        log_dynamodb_error("123", "TEST", "TEST MESSAGE")


def test_log_dynamodb_status_logs_status(job_record):
    log_dynamodb_status("1", "ABC", "TEST STATUS")

    job = [j for j in Jobs.scan()][0]

    assert job.Id == "1"
    assert job.StatusId == "TEST STATUS"


def test_log_dynamodb_no_job_for_status_logs_error(create_dynamodb_tables):
    with pytest.raises(Exception):
        log_dynamodb_status("1", "ABC", "TEST STATUS")


def test_success_ok():
    assert success("Custom message") == {"status": "success", "message": "Custom message"}
