from enum import Enum
from typing import List

import csv
import io

from utils.datetimezone import get_datetime_now


class RegistrationType(Enum):
    GP = "OnlyOnGP"
    PDS = "OnlyOnPDS"


def write_to_mem_csv(rows: List[str], header: List[str]) -> io.StringIO:
    """Writes a list of rows and header to an in-memory CSV string.

    Args:
        rows (List[str]): List of records to add to the CSV.
        header (List[str]): Header to add to the CSV.

    Returns:
        io.StringIO(): CSV string
    """
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=header)
    writer.writeheader()
    writer.writerows(rows)

    return stream


def get_registration_filename(practice_code: str, reg_type: RegistrationType) -> str:
    """Generate a registration diffs filename.

    Args:
        practice_code (str): GP practice code.
        reg_type (RegistrationType): Either 'RegistrationType.GP' or 'RegistrationType.PDS'
            indicating which dataset the records added to the file are exclusive to.

    Returns:
        str: Filename containing formatted practice, dataset name and datetime.
    """
    return f'{practice_code}-{reg_type.value}-{get_datetime_now().strftime("%Y%m%d%H%M%S")}.csv'
