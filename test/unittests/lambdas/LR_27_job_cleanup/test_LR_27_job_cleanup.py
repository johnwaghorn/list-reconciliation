import pytest

from conftest import JOB_ID, MOCK_REGISTRATIONS_OUTPUT_BUCKET
from utils.database.models import Jobs, InFlight
from utils.statuses import JobStatus


def test_validate_job_id(job_cleanup, create_job_item):
    """
    Validate Job ID is true when we find a matching id in the Jobs table
    """
    response = job_cleanup.validate_job_id(JOB_ID)
    expected = True
    assert response == expected


def test_validate_job_id_no_item(job_cleanup):
    """
    Validate Job ID is false when we don't find a matching id in the Jobs table
    """
    response = job_cleanup.validate_job_id(JOB_ID)
    expected = False
    assert response == expected


def test_maybe_delete_from_registrations_output_bucket(
    job_cleanup, upload_registration_outputs_to_s3, s3
):
    """
    Deleting from the LR-13 Registrations Output Bucket when there is a file in the bucket for this job
    """
    objects = s3.list_objects_v2(Bucket=MOCK_REGISTRATIONS_OUTPUT_BUCKET, Prefix=JOB_ID)
    response = len(objects["Contents"])
    expected = 3
    assert response == expected

    job_cleanup.maybe_delete_from_registrations_output_bucket(JOB_ID)

    with pytest.raises(KeyError):
        objects = s3.list_objects_v2(Bucket=MOCK_REGISTRATIONS_OUTPUT_BUCKET, Prefix=JOB_ID)
        return objects["Contents"]


def test_maybe_delete_from_registrations_output_bucket_no_files(job_cleanup, s3):
    """
    Deleting from the LR-13 Registrations OutputBucket when there is no file in the bucket for this job
    """
    with pytest.raises(KeyError):
        objects = s3.list_objects_v2(Bucket=MOCK_REGISTRATIONS_OUTPUT_BUCKET, Prefix=JOB_ID)
        return objects["Contents"]


def test_maybe_delete_from_inflight_table(job_cleanup, create_inflight_item):
    """
    Deleting from the InFlight table when there is an item for this job
    """
    response = InFlight.get(JOB_ID)
    expected = InFlight
    assert isinstance(response, expected)

    job_cleanup.maybe_delete_from_inflight_table(JOB_ID)

    with pytest.raises(InFlight.DoesNotExist):
        return InFlight.get(JOB_ID)


def test_maybe_delete_from_inflight_table_no_item(job_cleanup):
    """
    Deleting from the InFlight table when there is no item for this job
    """
    job_cleanup.maybe_delete_from_inflight_table(JOB_ID)

    with pytest.raises(InFlight.DoesNotExist):
        return InFlight.get(JOB_ID)


def test_update_job_status(job_cleanup, create_job_item):
    """
    Updating the Jobs table when there is an item for this job
    """
    jobs = Jobs.query(JOB_ID)
    for job in jobs:
        assert job.Id == JOB_ID
        assert job.StatusId == JobStatus.DEMOGRAPHICS_DIFFERENCES_PROCESSED.value

    job_cleanup.update_job_status(JOB_ID)

    jobs = Jobs.query(JOB_ID)
    for job in jobs:
        assert job.Id == JOB_ID
        assert job.StatusId == JobStatus.CLEANED_UP.value
