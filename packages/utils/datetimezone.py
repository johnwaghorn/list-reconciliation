from datetime import datetime
from pytz import timezone


def get_datetime_now(specified_timezone: str = "Europe/London") -> datetime:
    """Get current localized datetime

        Args:
            specified_timezone (str): Specified timezone to use in date localization

        Returns:
            datetime: Current localized datetime
    """

    return datetime.now(timezone(specified_timezone))


def localize_date(unlocalized_date: datetime = get_datetime_now(), specified_timezone: str = "Europe/London") -> datetime:
    """Localizes a specified datetime

        Args:
            unlocalized_date(datetime): Datetime to localize
            specified_timezone (str): Specified timezone to use in date localization

        Returns:
            datetime: Localized datetime
    """

    return timezone(specified_timezone).localize(unlocalized_date)
