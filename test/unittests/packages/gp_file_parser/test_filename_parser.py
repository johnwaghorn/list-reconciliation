import pytest
from datetime import datetime
from freezegun import freeze_time

from gp_file_parser.file_name_parser import (
    InvalidFilename,
    validate_filename,
)


@freeze_time("2020-02-01")
def test_validate_filename_valid_uppercase_filename_returns_valid_date():
    filename = "GPR4BRF1.B1A"

    expected = datetime.now(), "BRF"

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-02-01")
def test_validate_filename_valid_lowercase_filename_returns_valid_date():
    filename = "gpr4brf1.b1b"

    expected = datetime.now(), "BRF"

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-02-01")
def test_validate_filename_valid_mixcase_filename_returns_valid_date():
    filename = "gPr4brf1.B1c"

    expected = datetime.now(), "BRF"

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-02-01")
def test_validate_filename_no_filename_regex_match_raises_InvalidFilename():
    filename = "GDR4BRF1.B1A"

    with pytest.raises(InvalidFilename):
        validate_filename(filename)


@freeze_time("2020-02-01")
def test_validate_filename_no_extension_regex_match_raises_InvalidFilename():
    filename = "GPR4BRF1.B19"

    with pytest.raises(InvalidFilename):
        validate_filename(filename)


@freeze_time("2020-03-01")
def test_validate_filename_old_filedate_raises_InvalidFilename():
    filename = "GPR4BRF1.B1A"

    with pytest.raises(InvalidFilename):
        validate_filename(filename)


@freeze_time("2020-02-01")
def test_validate_filename_future_filedate_raises_InvalidFilename():
    filename = "GPR4BRF1.C1A"

    with pytest.raises(InvalidFilename):
        validate_filename(filename)


@freeze_time("2020-02-05")
def test_validate_filename_valid_month_indicator_parses_date_correctly():
    valid_month_indicator = "B"

    filename = f"GPR4BRF1.{valid_month_indicator}5A"

    expected = datetime.now(), "BRF"

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-12-15")
def test_validate_filename_valid_day_indicator_parses_date_correctly():
    valid_day_indicator = "F"

    filename = f"GPR4BRF1.L{valid_day_indicator}A"

    expected = datetime.now(), "BRF"

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-02-25")
def test_validate_filename_invalid_date_indicator_raises_ValueError():
    # BV = February 31
    invalid_date_indicator = "BV"

    filename = f"GPR4BRF1.{invalid_date_indicator[0]}{invalid_date_indicator[1]}A"

    with pytest.raises(ValueError):
        validate_filename(filename)


@freeze_time("2020-01-01")
def test_validate_filename_new_year_start_indicator_returns_valid_date():
    # LI = December 18
    filename = "GPR4BRF1.LIA"

    expected = datetime(2019, 12, 18), "BRF"

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-01-14")
def test_validate_filename_new_year_limit_indicator_returns_valid_date():
    # LV = December 31
    filename = "GPR4BRF1.LVA"

    expected = datetime(2019, 12, 31), "BRF"

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020, 01, 15")
def test_validate_filename_exceed_new_year_limit_raises_InvalidFilename():
    # LV = December 31
    filename = "GPR4BRF1.LVA"

    with pytest.raises(InvalidFilename):
        validate_filename(filename)


@freeze_time("2019, 12, 31")
def test_validate_filename_future_new_year_indicator_raises_InvalidFilename():
    # A1 = January 1
    filename = "GPR4BRF1.A1A"

    with pytest.raises(InvalidFilename):
        validate_filename(filename)
