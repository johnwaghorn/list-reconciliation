from datetime import datetime
from pytz import timezone, utc


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

    if unlocalized_date.tzinfo is not None and unlocalized_date.tzinfo.utcoffset(unlocalized_date) is not None:
        return unlocalized_date.astimezone(timezone(specified_timezone))

    else:
        return timezone(specified_timezone).localize(unlocalized_date)
