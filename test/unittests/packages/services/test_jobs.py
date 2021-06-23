from datetime import datetime

from moto import mock_dynamodb2
from pytz import timezone

import pytest

from services.jobs import get_job, JobNotFound
from utils.models import Jobs


@pytest.fixture
def dynamodb():
    with mock_dynamodb2():
        Jobs.create_table()
        yield


@pytest.fixture
def jobs(dynamodb):
    job = Jobs(
        "XYZ567",
        PracticeCode="Y123451",
        FileName="Y123451.E1A",
        StatusId="1",
        Timestamp=datetime(2021, 5, 27, 14, 48, 37, tzinfo=timezone("Europe/London")),
    )

    job.save()

    job = Jobs(
        "ABC123",
        PracticeCode="Y123452",
        FileName="Y123452.E1A",
        StatusId="1",
        Timestamp=datetime(2021, 5, 27, 14, 48, 37, tzinfo=timezone("Europe/London")),
    )

    job.save()
    yield


def test_get_job_job_exists(jobs):
    actual = get_job("ABC123")
    expected = Jobs.get("ABC123", "Y123452")

    assert actual.Id == expected.Id
    assert actual.PracticeCode == expected.PracticeCode


def test_get_job_job_doesnt_exist(jobs):
    with pytest.raises(JobNotFound):
        get_job("DEF")
