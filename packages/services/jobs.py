import pynamodb

from utils.models import Jobs


class JobNotFound(Exception):
    pass


def get_job(job_id: str) -> Jobs:
    """Gets a Job.

    Args:
        job_id (str): Job ID

    Returns:
        Jobs: Jobs item for job_id

    Raises:
        JobNotFound
    """

    try:
        return Jobs.query(job_id).next()
    except (StopIteration, pynamodb.exceptions.PutError):
        raise JobNotFound(f"JobId not found: {job_id}")
