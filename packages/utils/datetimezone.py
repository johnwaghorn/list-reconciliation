from datetime import datetime
from pytz import timezone


def get_datetime_now(specified_timezone: str = "Europe/London") -> datetime:
    return datetime.now(timezone(specified_timezone))
