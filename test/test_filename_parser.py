import pytest
from datetime import datetime
from freezegun import freeze_time

from file_name_parser.file_name_parser import (
    InvalidFilename,
    validate_filenames,
)


@freeze_time("2020-02-01")
def test_validate_filenames_valid_uppercase_filegroup_returns_valid_date():
    filegroup = [
        "GPR4BRF1.B1A",
        "GPR4BRF1.B1B",
        "GPR4BRF1.B1C",
    ]

    expected = datetime.now()

    actual = validate_filenames(filegroup)

    assert expected == actual


@freeze_time("2020-02-01")
def test_validate_filenames_valid_lowercase_filegroup_returns_valid_date():
    filegroup = [
        "gpr4brf1.b1a",
        "gpr4brf1.b1b",
        "gpr4brf1.b1c",
    ]

    expected = datetime.now()

    actual = validate_filenames(filegroup)

    assert expected == actual


@freeze_time("2020-02-01")
def test_validate_filenames_valid_mixcase_filegroup_returns_valid_date():
    filegroup = [
        "Gpr4brf1.b1A",
        "gpR4brf1.b1b",
        "gPr4brf1.B1c",
    ]

    expected = datetime.now()

    actual = validate_filenames(filegroup)

    assert expected == actual


@freeze_time("2020-02-01")
def test_validate_filenames_filegroup_not_identical_raises_InvalidFilename():
    filegroup = [
        "GPR4BRF1.B1A",
        "GPR4BRF1.B1B",
        "GPR4ARF1.B1C",
    ]

    with pytest.raises(InvalidFilename):
        validate_filenames(filegroup)


@freeze_time("2020-02-01")
def test_validate_filenames_extension_duplicates_raises_InvalidFilename():
    filegroup = [
        "GPR4BRF1.B1A",
        "GPR4BRF1.B1A",
        "GPR4BRF1.B1A",
    ]

    with pytest.raises(InvalidFilename):
        validate_filenames(filegroup)


@freeze_time("2020-02-01")
def test_validate_filenames_extensions_not_sequential_raises_InvalidFilename():
    filegroup = [
        "GPR4BRF1.B1A",
        "GPR4BRF1.B1X",
        "GPR4BRF1.B1G",
    ]

    with pytest.raises(InvalidFilename):
        validate_filenames(filegroup)


@freeze_time("2020-02-01")
def test_validate_filenames_no_filename_regex_match_raises_InvalidFilename():
    filegroup = [
        "GDR4BRF1.B1A",
        "GDR4BRF1.B1B",
        "GDR4BRF1.B1C",
    ]

    with pytest.raises(InvalidFilename):
        validate_filenames(filegroup)


def test_validate_filenames_no_extension_regex_match_raises_InvalidFilename():
    filegroup = [
        "GPR4BRF1.ZZA",
        "GPR4BRF1.ZZB",
    ]

    with pytest.raises(InvalidFilename):
        validate_filenames(filegroup)


@freeze_time("2020-03-01")
def test_validate_filenames_old_filedate_raises_InvalidFilename():
    filegroup = [
        "GPR4BRF1.B1A",
        "GPR4BRF1.B1B",
        "GPR4BRF1.B1C",
    ]

    with pytest.raises(InvalidFilename):
        validate_filenames(filegroup)


@freeze_time("2020-02-01")
def test_validate_filenames_future_filedate_raises_InvalidFilename():
    filegroup = [
        "GPR4BRF1.C1A",
        "GPR4BRF1.C1B",
        "GPR4BRF1.C1C",
    ]

    with pytest.raises(InvalidFilename):
        validate_filenames(filegroup)


@freeze_time("2020-02-05")
def test_validate_filenames_valid_month_indicator_parses_date_correctly():
    valid_month_indicator = "B"

    filegroup = [f"GPR4BRF1.{valid_month_indicator}5A"]

    expected = datetime.now()

    actual = validate_filenames(filegroup)

    assert expected == actual


@freeze_time("2020-12-15")
def test_validate_filenames_valid_day_indicator_parses_date_correctly():
    valid_day_indicator = "F"

    filegroup = [f"GPR4BRF1.L{valid_day_indicator}A"]

    expected = datetime.now()

    actual = validate_filenames(filegroup)

    assert expected == actual


@freeze_time("2020-02-25")
def test_validate_filenames_invalid_date_indicator_raises_ValueError():
    # BV = February 31
    invalid_date_indicator = "BV"

    filegroup = [
        f"GPR4BRF1.{invalid_date_indicator[0]}{invalid_date_indicator[1]}A",
    ]

    with pytest.raises(ValueError):
        validate_filenames(filegroup)


@freeze_time("2020-01-01")
def test_validate_filenames_new_year_start_indicator_returns_valid_date():
    # LI = December 18
    filegroup = [
        "GPR4BRF1.LIA",
        "GPR4BRF1.LIB",
        "GPR4BRF1.LIC",
    ]

    expected = datetime(2019, 12, 18)

    actual = validate_filenames(filegroup)

    assert expected == actual


@freeze_time("2020-01-14")
def test_validate_filenames_new_year_limit_indicator_returns_valid_date():
    # LV = December 31
    filegroup = [
        "GPR4BRF1.LVA",
        "GPR4BRF1.LVB",
        "GPR4BRF1.LVC",
    ]

    expected = datetime(2019, 12, 31)

    actual = validate_filenames(filegroup)

    assert expected == actual


@freeze_time("2020, 01, 15")
def test_validate_filenames_exceed_new_year_limit_raises_InvalidFilename():
    # LV = December 31
    filegroup = [
        "GPR4BRF1.LVA",
        "GPR4BRF1.LVB",
        "GPR4BRF1.LVC",
    ]

    with pytest.raises(InvalidFilename):
        validate_filenames(filegroup)


@freeze_time("2019, 12, 31")
def test_validate_filenames_future_new_year_indicator_raises_InvalidFilename():
    # A1 = January 1
    filegroup = [
        "GPR4BRF1.A1A",
        "GPR4BRF1.A1B",
        "GPR4BRF1.A1C",
    ]

    with pytest.raises(InvalidFilename):
        validate_filenames(filegroup)
