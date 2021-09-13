import pytest
from jobs.statuses import JobStatus


@pytest.mark.parametrize(
    "code,value",
    [(JobStatus.VALIDATED_AND_QUEUED, "1"), (JobStatus.RECORDS_PROCESSED, "2")],
)
def test_statuses_have_correct_value(code, value):
    assert code.value == value
