import datetime

import pytest
from moto import mock_dynamodb2
from spine_aws_common.lambda_application import LambdaApplication


from utils.database.models import Jobs
from utils.logger import log_dynamodb_status, success
from utils.datetimezone import localize_date


@pytest.fixture
def spine_logger():
    app = LambdaApplication()
    return app.log_object


@pytest.fixture
def create_dynamodb_tables():
    with mock_dynamodb2():
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


def test_log_dynamodb_status_logs_status(job_record, spine_logger):
    log_dynamodb_status(spine_logger, "1", "ABC", "TEST STATUS")

    job = [j for j in Jobs.scan()][0]

    assert job.Id == "1"
    assert job.StatusId == "TEST STATUS"


def test_log_dynamodb_no_job_for_status_logs_error(create_dynamodb_tables, spine_logger):
    with pytest.raises(Exception):
        log_dynamodb_status(spine_logger, "1", "ABC", "TEST STATUS")


def test_success_ok():
    assert success("Custom message") == {
        "status": "success",
        "message": "Custom message",
    }
