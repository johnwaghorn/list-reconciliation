import io

from freezegun import freeze_time

import pytest

from utils import get_registration_filename, RegistrationType, write_to_mem_csv


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


@pytest.mark.parametrize(
    "rows,header,expected,name",
    [
        (
            [
                {
                    "col a": "Content",
                    "col b": "string,containing,commas",
                    "1": "",
                    "2": None,
                },
                {"col a": "1", "col b": "2", "1": "3", "2": None},
            ],
            ["col a", "col b", "1", "2"],
            """col a,col b,1,2\nContent,"string,containing,commas",,\n1,2,3,\n""",
            "Header with records; one column contains commas.",
        ),
        (
            [],
            ["col a", "col b", "1", "2"],
            "col a,col b,1,2\n",
            "Header with no records",
        ),
        ([], [], "\n", "No header with no records"),
    ],
)
def test_write_to_mem_csv(rows, header, expected, name):
    actual = write_to_mem_csv(rows, header)

    assert actual.getvalue() == io.StringIO(expected).getvalue(), name
