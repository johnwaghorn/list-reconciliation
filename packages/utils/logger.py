from typing import Dict
from uuid import uuid4

import logging
import sys
import traceback

from utils.models import Errors, Jobs
from utils.datetimezone import get_datetime_now

VALIDATION_ERROR = "VALIDATION_ERROR"
UNHANDLED_ERROR = "UNHANDLED_ERROR"


LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


def log_dynamodb_error(job_id: str, name: str, msg: str) -> Dict:
    """Log an error to DynamoDB for the List Reconciliation process.

    Args:
        job_id (str): ID of the job to log the error for.
        name (str): Name of the error to log.
        msg (str): Error message to log.
    """

    error_id = str(uuid4())
    tb = traceback.format_exc()
    LOG.exception(f"JobId: {job_id}, error_id: {error_id}, {msg}")
    try:
        type_ = sys.exc_info()[0].__name__

    except AttributeError:
        type_ = name

    try:
        item = Errors(
            error_id,
            JobId=job_id,
            Type=type_,
            Name=name,
            Description=msg,
            Traceback=tb,
            Timestamp=get_datetime_now(),
        )
        item.save()

    except Exception:
        LOG.exception(f"JobId: {job_id}, Unable to log error to Errors table")
        raise

    return {"status": "error", "message": msg, "error_id": error_id, "traceback": tb}


def log_dynamodb_status(job_id: str, practice_code: str, status: str) -> Dict:
    """Update a status to DynamoDB for the List Reconciliation process.

    Args:
        job_id (str): ID of the job to log the error for.
        status (str): Status message to log.
    """

    try:
        item = Jobs.get(job_id, practice_code)
        item.update(actions=[Jobs.StatusId.set(status)])
        item.save()

    except Exception:
        log_dynamodb_error(job_id, "StatusLogError", f"Unable to log status to Jobs table")
        raise

    return success("Updated status")


def success(message: str) -> Dict[str, str]:
    """Create a success message as a dictionary.

    Args:
        message (str): Message to add.

    Returns:
        Dict[str, str]
    """

    return {"status": "success", "message": message}
