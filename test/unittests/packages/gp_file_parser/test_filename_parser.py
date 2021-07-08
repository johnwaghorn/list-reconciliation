import pytest

from datetime import datetime
from freezegun import freeze_time

from gp_file_parser.file_name_parser import (
    InvalidFilename,
    validate_filename,
)


@freeze_time("2020-02-01")
def test_validate_filename_valid_uppercase_filename_returns_valid_date():
    filename = "A82023_GPR4BRF1.B1A"

    expected = {"extract_date": datetime.now(), "practice_code": "A82023", "ha_cipher": "BRF"}

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-02-01")
def test_validate_filename_valid_lowercase_filename_returns_valid_date():
    filename = "a82023_gpr4brf1.b1b"

    expected = {"extract_date": datetime.now(), "practice_code": "A82023", "ha_cipher": "BRF"}

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-02-01")
def test_validate_filename_valid_mixcase_filename_returns_valid_date():
    filename = "A82023_gPr4brf1.B1c"

    expected = {"extract_date": datetime.now(), "practice_code": "A82023", "ha_cipher": "BRF"}

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-02-01")
def test_validate_filename_invalid_format_raises_InvalidFilename():
    filename = "A12023GPR4BRF1.B1A"

    expected = "Filename does not have the correct format"

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert str(exc.value) == expected


@freeze_time("2020-02-01")
def test_validate_filename_invalid_characters_raises_InvalidFilename():
    filename = "A12023-GPR4BRF1.B1A"

    expected = "Filename contains invalid characters"

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert str(exc.value) == expected


@freeze_time("2020-02-01")
def test_validate_filename_exceeds_length_raises_InvalidFilename():
    filename = "A12023___GPR4BRF1__.B1A"

    expected = "Filename exceeds character limit"

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert str(exc.value) == expected


@freeze_time("2020-02-01")
def test_validate_filename_invalid_gp_code_match_raises_InvalidFilename():
    filename = "AZ2023_GPR4BRF1.B1A"

    expected = "Filename contains invalid practice code"

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert str(exc.value) == expected


@freeze_time("2020-02-01")
def test_validate_filename_invalid_gp_code_and_invalid_filename_raises_InvalidFilename():
    filename = "AZ2023_GAR4BRF1.CSA"

    expected = (
        "Filename contains invalid practice code\n"
        "Filename contains invalid DOW name and/or HA cipher"
    )

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert str(exc.value) == expected


@freeze_time("2020-02-01")
def test_validate_filename_all_invalid_raises_InvalidFilename():
    filename = "AZ2023_GAR4BRF1.ZZZ"

    expected = (
        "Filename contains invalid practice code\n"
        "Filename contains invalid DOW name and/or HA cipher\n"
        "Filename contains invalid extension"
    )

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert str(exc.value) == expected


@freeze_time("2020-02-01")
def test_validate_filename_no_filename_regex_match_raises_InvalidFilename():
    filename = "A82023_GDR4BRF1.B1A"

    expected = "Filename contains invalid DOW name and/or HA cipher"

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert str(exc.value) == expected


@freeze_time("2020-02-01")
def test_validate_filename_no_extension_regex_match_raises_InvalidFilename():
    filename = "A82023_GPR4BRF1.B19"

    expected = "Filename contains invalid extension"

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert str(exc.value) == expected


@freeze_time("2020-03-01")
def test_validate_filename_old_filedate_raises_InvalidFilename():
    filename = "A82023_GPR4BRF1.B1A"

    expected = "File date must not be older than 14 days"

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert str(exc.value) == expected


@freeze_time("2020-02-01")
def test_validate_filename_future_filedate_raises_InvalidFilename():
    filename = "A82023_GPR4BRF1.C1A"

    expected = "File date must not be from the future"

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert str(exc.value) == expected


@freeze_time("2020-02-05")
def test_validate_filename_valid_month_indicator_parses_date_correctly():
    valid_month_indicator = "B"

    filename = f"A82023_GPR4BRF1.{valid_month_indicator}5A"

    expected = {"extract_date": datetime.now(), "practice_code": "A82023", "ha_cipher": "BRF"}

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-12-15")
def test_validate_filename_valid_day_indicator_parses_date_correctly():
    valid_day_indicator = "F"

    filename = f"A82023_GPR4BRF1.L{valid_day_indicator}A"

    expected = {"extract_date": datetime.now(), "practice_code": "A82023", "ha_cipher": "BRF"}

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-02-25")
def test_validate_filename_invalid_date_indicator_raises_ValueError():
    # BV = February 31
    invalid_date_indicator = "BV"

    filename = f"A82023_GPR4BRF1.{invalid_date_indicator[0]}{invalid_date_indicator[1]}A"

    expected = "Filename contains invalid date"

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert str(exc.value) == expected


@freeze_time("2020-01-01")
def test_validate_filename_new_year_start_indicator_returns_valid_date():
    # LI = December 18
    filename = "A82023_GPR4BRF1.LIA"

    expected = {"extract_date": datetime(2019, 12, 18), "practice_code": "A82023", "ha_cipher": "BRF"}

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-01-14")
def test_validate_filename_new_year_limit_indicator_returns_valid_date():
    # LV = December 31
    filename = "A82023_GPR4BRF1.LVA"

    expected = {"extract_date": datetime(2019, 12, 31), "practice_code": "A82023", "ha_cipher": "BRF"}

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020, 01, 15")
def test_validate_filename_exceed_new_year_limit_raises_InvalidFilename():
    # LV = December 31
    filename = "A82023_GPR4BRF1.LVA"

    expected = "File date must not be from the future"

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert str(exc.value) == expected


@freeze_time("2019, 12, 31")
def test_validate_filename_future_new_year_indicator_raises_InvalidFilename():
    # A1 = January 1
    filename = "A82023_GPR4BRF1.A1A"

    expected = "File date must not be older than 14 days"

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert str(exc.value) == expected
