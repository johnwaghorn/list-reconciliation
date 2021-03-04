import re
from datetime import datetime
from typing import List


class InvalidFilename(Exception):
    pass


def validate_filenames(file_group: List[str]) -> datetime.date:
    """Validates a list of filenames and returns the file group date

    Checks the following rules:
        - Filenames must match expression
        - File extension must match expression
        - Dates must not exceed the current date
        - Date must not be older than 14 days

    Args:
        file_group (List): List of filenames

    Returns:
        extract_date (date): Formatted date

    Raises:
        InvalidFilename: Raised when filename doesn't match expressions/
                         Raised when invalid dates contained within filename
    """
    
    FILENAME_EX = "^GPR4([A-Z0-9]{3})1"

    EXTENSION_EX = "([A-L][1-9A-V])[A-Z]$"

    if len({f[:-1] for f in file_group}) != 1:
        raise InvalidFilename("All filenames must be identical up to the penultimate character")

    file_ids = "".join(sorted([f[-1] for f in file_group]))

    if file_ids not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" or not file_ids.startswith("A"):
        raise InvalidFilename("File extension identifiers must be sequential, starting from 'A'")

    valid_names = [re.search(FILENAME_EX, extract) for extract in file_group]

    if not valid_names or not all(valid_names):
        raise InvalidFilename("All filenames must have the correct format")

    valid_extensions = [re.search(EXTENSION_EX, extract) for extract in file_group]

    if not valid_extensions or not all(valid_extensions):
        raise InvalidFilename("All filenames must have the correct extension format")

    date_indicator = valid_extensions[0].group(1)

    months = "ABCDEFGHIJKL"
    days = "123456789ABCDEFGHIJKLMNOPQRSTUV"

    month_code = date_indicator[0]
    month = months.index(month_code) + 1

    day_code = date_indicator[1]
    day = days.index(day_code) + 1

    date_now = datetime.now()

    new_year_start_limit = datetime(date_now.year, 1, 1)
    new_year_end_limit = datetime(date_now.year, 1, 15)

    # If current date is between Jan 1-15, treats extract codes from Dec 18-31 as previous year
    if date_now >= new_year_start_limit and date_now < new_year_end_limit:
        if month_code == "L" and day_code in "IJKLMNOPQRSTUV":
            extract_date = datetime(date_now.year - 1, month, day).date()
    else:
        try:
            extract_date = datetime(date_now.year, month, day).date()
        except:
            raise ValueError("The date within the filename is not a valid date")

    days_difference = (date_now.date() - extract_date).days

    if days_difference < 0:
        raise InvalidFilename("File date must not be from the future")
    elif days_difference > 14:
        raise InvalidFilename("File date must not be older than 14 days")

    return extract_date
