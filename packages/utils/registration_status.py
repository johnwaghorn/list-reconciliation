from enum import Enum
from typing import Dict


class GPRegistrationStatus(Enum):
    UNMATCHED = "Unmatched"
    MATCHED = "Matched"
    PARTNERSHIP_MISMATCH = "Partnership Mismatch"
    DEDUCTED_PATIENT_MATCH = "Deducted Patient Match"


def get_gp_registration_status(gp_gpcode: str, pds_record: Dict) -> GPRegistrationStatus:
    """Determine the GP registration status given a GP file gp code and a pds record.

    Args:
        gp_gpcode (str): GP file gp code.
        pds_record (Dict): PDS record

    Returns:
        GPRegistrationStatus
    """

    if not pds_record:
        return GPRegistrationStatus.UNMATCHED.value

    if pds_record["gp_code"]:
        if gp_gpcode == pds_record["gp_code"]:
            return GPRegistrationStatus.MATCHED.value
        else:
            return GPRegistrationStatus.PARTNERSHIP_MISMATCH.value

    return GPRegistrationStatus.DEDUCTED_PATIENT_MATCH.value
