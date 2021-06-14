from freezegun import freeze_time

import pytest

from utils import get_registration_filename, RegistrationType


@freeze_time("2020-02-01 13:40:00")
@pytest.mark.parametrize(
    "practice,type_,expected",
    [
        ("ABC123", RegistrationType.GP, "ABC123-OnlyOnGP-20200201134000.csv"),
        ("ABC123", RegistrationType.PDS, "ABC123-OnlyOnPDS-20200201134000.csv"),
    ],
)
def test_get_registration_filename(practice, type_, expected):
    actual = get_registration_filename(practice, type_)

    assert actual == expected
