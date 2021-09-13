from enum import Enum


class JobStatus(Enum):
    VALIDATED_AND_QUEUED = "1"
    RECORDS_PROCESSED = "2"
    COMPLETE = "3"
    SENDER_NOTIFIED_VALIDATION_FAILED = "10"
    TIMED_OUT = "11"
    CLEANED_UP = "12"


class InvalidErrorType(Enum):
    RECORDS = "INVALID_RECORDS"
    STRUCTURE = "INVALID_STRUCTURE"
    FILENAME = "INVALID_FILENAME"


class InputFolderType(Enum):
    IN = "inbound/"
    PASS = "pass/"
    FAIL = "fail/"
    RETRY = "retry/"


class RegistrationType(Enum):
    GP = "OnlyOnGP"
    PDS = "OnlyOnPDS"


class JobNotFound(Exception):
    """Job Not Found Exception"""
