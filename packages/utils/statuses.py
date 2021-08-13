from enum import Enum


class JobStatus(Enum):
    ADDED_TO_QUEUE = "1"  # LR-02 1 Validated and queued
    PDS_FHIR_API_PROCESSED = "2"  # LR-09 2 Job Records Processed
    DEMOGRAPHICS_DIFFERENCES_PROCESSED = "3"  # LR-14 3 Job Complete
    SENDER_NOTIFIED_VALIDATION_FAILED = "10"  # LR-04 10 Sender notified validation failed
    TIMED_OUT = "11"  # LR-09 11 Job timed out
    CLEANED_UP = "12"  # LR-27 12 Cleaned up job
