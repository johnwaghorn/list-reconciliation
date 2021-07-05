import datetime
import pytest

from datetime import datetime
from freezegun import freeze_time
from pytz import timezone

from utils.datetimezone import get_datetime_now, localize_date


@freeze_time("2020-02-01 03:21:34")
def test_get_datetime_now_returns_correct_time():
    actual = get_datetime_now()

    assert actual.year == 2020
    assert actual.month == 2
    assert actual.day == 1
    assert actual.hour == 3
    assert actual.minute == 21
    assert actual.second == 34
    assert actual.tzinfo.tzname(actual) == "GMT"


@freeze_time("2020-02-01 12:21:34")
@pytest.mark.parametrize(
    "timezone,year,month,day,hour,minute,second",
    [
        ("UTC", 2020, 2, 1, 12, 21, 34),
        ("US/Central", 2020, 2, 1, 6, 21, 34),
        ("US/Eastern", 2020, 2, 1, 7, 21, 34),
        ("GMT", 2020, 2, 1, 12, 21, 34),
        ("Europe/Amsterdam", 2020, 2, 1, 13, 21, 34),
        ("Europe/Vatican", 2020, 2, 1, 13, 21, 34),
        ("Pacific/Pago_Pago", 2020, 2, 1, 1, 21, 34),
        ("America/Thunder_Bay", 2020, 2, 1, 7, 21, 34),
        ("Asia/Hong_Kong", 2020, 2, 1, 20, 21, 34)
    ],
)
def test_get_datetime_now_with_different_timezone_returns_correct_time(
    timezone: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int
):
    actual = get_datetime_now(timezone)

    assert actual.year == year
    assert actual.month == month
    assert actual.day == day
    assert actual.hour == hour
    assert actual.minute == minute
    assert actual.second == second
    assert actual.tzinfo.zone == timezone


def test_get_datetime_now_returns_correct_type():
    actual = get_datetime_now()

    assert type(actual) == datetime


@freeze_time("2021-05-07T14:30:00.000000+0000")
def test_localize_date_without_tz_returns_correct_date():
    expected_year = 2021
    expected_month = 5
    expected_day = 7
    expected_hour = 14
    expected_minute = 30
    expected_second = 0
    expected_tz = "Europe/London"

    actual = localize_date(datetime.now())

    assert actual.year == expected_year
    assert actual.month == expected_month
    assert actual.day == expected_day
    assert actual.hour == expected_hour
    assert actual.minute == expected_minute
    assert actual.second == expected_second
    assert actual.tzinfo.zone == expected_tz


@freeze_time("2021-05-07T14:30:00.000000-0400")
def test_localize_date_with_tz_returns_correct_date():
    expected_year = 2021
    expected_month = 5
    expected_day = 7
    expected_hour = 19
    expected_minute = 30
    expected_second = 0
    expected_tz = "Europe/London"

    actual = localize_date(datetime.now(timezone("US/Eastern")))

    assert actual.year == expected_year
    assert actual.month == expected_month
    assert actual.day == expected_day
    assert actual.hour == expected_hour
    assert actual.minute == expected_minute
    assert actual.second == expected_second
    assert actual.tzinfo.zone == expected_tz
