from datetime import datetime

from jobs.statuses import RegistrationType


def get_registration_filename(practice_code: str, reg_type: RegistrationType) -> str:
    """Generate a registration diffs filename.

    Args:
        practice_code (str): GP practice code.
        reg_type (RegistrationType): Either 'RegistrationType.GP' or 'RegistrationType.PDS'
            indicating which dataset the records added to the file are exclusive to.

    Returns:
        str: Filename containing formatted practice, dataset name and datetime.
    """
    return f'{practice_code}-{reg_type.value}-{datetime.now().strftime("%Y%m%d%H%M%S")}.csv'
