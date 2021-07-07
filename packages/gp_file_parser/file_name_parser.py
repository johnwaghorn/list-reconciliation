import re

from datetime import datetime
from typing import Tuple

from utils.datetimezone import get_datetime_now, localize_date


class InvalidFilename(Exception):
    pass


def validate_filename(
    filename: str, process_datetime: datetime = None
) -> Tuple[datetime, str]:
    """Validates a GP extract filename

    Checks the following rules:
        - Filename must match expression
        - File extension must match expression
        - Date must not exceed the current date
        - Date must not be older than 14 days

    Args:
        filename (str): GP extract filename
        process_datetime (datetime): Time of processing.

    Returns:
        Tuple: extract date (date), HA cipher (str)

    Raises:
        InvalidFilename: Raised when filename doesn't match expressions/
                         Raised when invalid dates contained within filename
    """

    filename = filename.upper()

    valid_name = re.search(r"^GPR4([A-Z0-9]{3})1", filename)

    if not valid_name:
        raise InvalidFilename("Filename must have the correct format")

    valid_extension = re.search(r"([A-L][1-9A-V])[A-Z]$", filename)

    if not valid_extension:
        raise InvalidFilename("Filename must have the correct extension format")

    date_indicator = valid_extension.group(1)

    months = "ABCDEFGHIJKL"
    month_code = date_indicator[0]
    extract_month = months.index(month_code) + 1

    days = "123456789ABCDEFGHIJKLMNOPQRSTUV"
    day_code = date_indicator[1]
    extract_day = days.index(day_code) + 1

    date_now = process_datetime or get_datetime_now()

    new_year_start_limit = localize_date(datetime(date_now.year, 1, 1))
    new_year_end_limit = localize_date(datetime(date_now.year, 1, 15))

    # If current date is between Jan 1-15, treats extract codes from Dec 18-31 as previous year
    if date_now >= new_year_start_limit and date_now < new_year_end_limit:
        if month_code == "L" and day_code in "IJKLMNOPQRSTUV":
            extract_date = datetime(date_now.year - 1, extract_month, extract_day)
    else:
        try:
            extract_date = datetime(date_now.year, extract_month, extract_day)
        except Exception:
            raise ValueError("The date within the filename is not a valid date")

    days_difference = (date_now.date() - extract_date.date()).days

    if days_difference < 0:
        raise InvalidFilename("File date must not be from the future")
    elif days_difference > 14:
        raise InvalidFilename("File date must not be older than 14 days")

    ha_cipher = filename[4:7]

    return extract_date, ha_cipher
