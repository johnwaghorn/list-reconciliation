import sys
import traceback
from datetime import datetime
from typing import Dict
from uuid import uuid4

import logging
import sys
import traceback

from utils.database.models import Errors, Jobs

from utils.datetimezone import get_datetime_now


VALIDATION_ERROR = "VALIDATION_ERROR"
UNHANDLED_ERROR = "UNHANDLED_ERROR"

Success = Dict[str, str]


def log_dynamodb_error(
    logger: object,
    job_id: str,
    name: str,
    msg: str,
    time: datetime = get_datetime_now(),
) -> Dict:
    """Log an error to DynamoDB for the List Reconciliation process.

    Args:
        logger: LambdaBase class logger
        job_id (str): ID of the job to log the error for.
        name (str): Name of the error to log.
        msg (str): Error message to log.
        time (datetime): Time of error, optional, will be populated if not provided.
    """

    error_id = str(uuid4())
    tb = traceback.format_exc()
    logger.write_log(
        "UTI9997",
        None,
        {
            "logger": "Dynamo",
            "level": "Error",
            "message": f"JobId: {job_id}, error_id: {error_id}, {msg}",
        },
    )
    try:
        type_ = sys.exc_info()[0].__name__

    except AttributeError:
        type_ = name

    try:
        item = Errors(
            error_id,
            JobId=job_id or "99999999-0909-0909-0909-999999999999",
            Type=type_,
            Name=name,
            Description=msg,
            Traceback=tb,
            Timestamp=time,
        )
        item.save()

    except Exception:
        log_message = f"JobId: {job_id}, Unable to log error to Errors table"
        logger.write_log(
            "UTI9997",
            tb,
            {"logger": "Dynamo", "level": "ERROR", "message": log_message},
        )

        raise

    return {"status": "error", "message": msg, "error_id": error_id, "traceback": tb}


def log_dynamodb_status(logger: object, job_id: str, practice_code: str, status: str) -> Success:
    """Update a status to DynamoDB for the List Reconciliation process.

    Args:
        logger (object): Base class logger
        job_id (str): ID of the job to log the error for.
        practice_code (str): GP practice code
        status (str): Status message to log.
    """

    try:
        item = Jobs.get(job_id, practice_code)
        item.update(actions=[Jobs.StatusId.set(status)])
        item.save()

    except Exception:
        log_dynamodb_error(
            logger,
            job_id,
            "StatusLogError",
            f"Unable to log status to Jobs table",
        )
        raise

    return success("Updated status")


def success(message: str) -> Success:
    """Create a success message as a dictionary.

    Args:
        message (str): Message to add.

    Returns:
        Success
    """

    return {"status": "success", "message": message}
