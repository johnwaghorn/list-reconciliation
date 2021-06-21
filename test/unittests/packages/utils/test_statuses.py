from utils.statuses import JobStatus
import pytest


@pytest.mark.parametrize(
    "code,value",
    [
        (JobStatus.ADDED_TO_QUEUE, "1"),
        (JobStatus.PDS_FHIR_API_PROCESSED, "2")
    ]
)
def test_statuses_have_correct_value(code, value):
    assert code.value == value