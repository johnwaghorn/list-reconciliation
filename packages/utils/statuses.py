from enum import Enum


class JobStatus(Enum):
    VALIDATED_AND_QUEUED = "1"
    RECORDS_PROCESSED = "2"
    COMPLETE = "3"
    SENDER_NOTIFIED_VALIDATION_FAILED = "10"
    TIMED_OUT = "11"
    CLEANED_UP = "12"
