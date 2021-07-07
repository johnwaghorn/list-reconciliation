from datetime import datetime

import pytest
from freezegun import freeze_time
from pynamodb.constants import DATETIME_FORMAT

from utils.database.attributes import GMTDateTimeAttribute
from utils.datetimezone import get_datetime_now


@freeze_time("2020-04-06T04:40:00.000000+0100")
def test_serialize_parses_get_datetime_now_correctly():
    instance = GMTDateTimeAttribute()
    expected = "2020-04-06T04:40:00.000000+0100"

    actual = instance.serialize(get_datetime_now())

    assert isinstance(actual, str)

    assert expected == actual


@freeze_time("2020-04-06T04:40:00.000000")
def test_serialize_parses_datetime_now_correctly():
    instance = GMTDateTimeAttribute()
    expected = "2020-04-06T04:40:00.000000+0100"

    actual = instance.serialize(datetime.now())

    assert isinstance(actual, str)

    assert expected == actual


@freeze_time("2020-04-06T04:40:00.000000")
def test_serialize_rejects_incorrect_timezones():
    with pytest.raises(ValueError) as error:
        instance = GMTDateTimeAttribute()
        instance.serialize(get_datetime_now("Pacific/Pago_Pago"))

    assert error is not None
    assert (
        error.value.args[0]
        == "Datetime string '2020-04-05 17:40:00-11:00' with timezone 'SST' doesn't use the correct timezone 'BST'"
    )


@freeze_time("2020-04-06T04:40:00.000000+0100")
def test_deserialize_parses_string_correctly():
    instance = GMTDateTimeAttribute()
    expected = get_datetime_now()

    actual = instance.deserialize("2020-04-06T04:40:00.000000+0100")

    assert isinstance(actual, datetime)

    assert expected.year == actual.year
    assert expected.month == actual.month
    assert expected.day == actual.day
    assert expected.hour == actual.hour
    assert expected.second == actual.second
    assert expected.tzname() == actual.tzname()


@pytest.mark.parametrize(
    "input",
    [([]), (3), ((4, 5)), (True)],
)
def test_deserialize_rejects_none_datetime_type(input):
    with pytest.raises(ValueError) as error:
        instance = GMTDateTimeAttribute()
        instance.deserialize(input)

    assert error is not None
    assert (
        error.value.args[0]
        == f"Datetime string '{input}' does not match format '{DATETIME_FORMAT}'"
    )


@pytest.mark.parametrize(
    "input",
    [
        ("bad length"),
        ("2020x04-06T04:40:00.000000+0100"),
        ("2020-04x06T04:40:00.000000+0100"),
        ("2020-04-06x04:40:00.000000+0100"),
        ("2020-04-06T04x40:00.000000+0100"),
        ("2020-04-06T04:40x00.000000+0100"),
        ("2020-04-06T04:40:00x000000+0100"),
        ("2020-04-06T04:40:00.000000x0100"),
    ],
)
def test_deserialize_rejects_incorrect_formatting(input):
    with pytest.raises(ValueError) as error:
        instance = GMTDateTimeAttribute()
        instance.deserialize(input)

    assert error is not None
    assert (
        error.value.args[0]
        == f"Datetime string '{input}' does not match format '{DATETIME_FORMAT}'"
    )
