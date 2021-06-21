from enum import Enum


class JobStatus(Enum):
    ADDED_TO_QUEUE = "1"
    PDS_FHIR_API_PROCESSED = "2"