import pytest

from datetime import datetime
from freezegun import freeze_time

from gp_file_parser.file_name_parser import validate_filename
from lr_logging.exceptions import InvalidFilename


@freeze_time("2020-02-01")
def test_validate_filename_valid_uppercase_filename_returns_valid():
    filename = "A82023_GPR4BRF1.B1A.DAT"

    expected = {
        "filename": "A82023_GPR4BRF1.B1A",
        "extract_date": datetime.now(),
        "practice_code": "A82023",
        "ha_cipher": "BRF",
    }

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-02-01")
def test_validate_filename_valid_lowercase_filename_returns_valid():
    filename = "a82023_gpr4brf1.b1b"

    expected = {
        "filename": "A82023_GPR4BRF1.B1B",
        "extract_date": datetime.now(),
        "practice_code": "A82023",
        "ha_cipher": "BRF",
    }

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-02-01")
def test_validate_filename_valid_mixcase_filename_returns_valid():
    filename = "A82023_gPr4brf1.B1c.dAt"

    expected = {
        "filename": "A82023_GPR4BRF1.B1C",
        "extract_date": datetime.now(),
        "practice_code": "A82023",
        "ha_cipher": "BRF",
    }

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-02-01")
def test_validate_filename_invalid_format_raises_InvalidFilename():
    filename = "A12023GPR4BRF1.B1A"

    expected = {"message": ["Filename does not have the correct format"]}

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert exc.value.args[0] == expected


@freeze_time("2020-02-01")
def test_validate_filename_invalid_characters_raises_InvalidFilename():
    filename = "AZ2023-GPR4BRF1.B1A"

    expected = {"message": ["Filename contains invalid characters"]}

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert exc.value.args[0] == expected


@freeze_time("2020-02-01")
def test_validate_filename_exceeds_length_raises_InvalidFilename():
    filename = "A12023___GPR4BRF1__.B1A"

    expected = {"message": ["Filename exceeds character limit"]}

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert exc.value.args[0] == expected


@freeze_time("2020-02-01")
def test_validate_filename_invalid_gp_practicecode_match_raises_InvalidFilename():
    filename = "AZ2023_GPR4BRF1.B1A"

    expected = {"message": ["Filename contains invalid practice code"]}

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert exc.value.args[0] == expected


@freeze_time("2020-02-01")
def test_validate_filename_invalid_gp_practicecode_and_invalid_filename_raises_InvalidFilename():
    filename = "AZ2023_GAR4BRF1.CSA.DAT"

    expected = {
        "message": [
            "Filename contains invalid practice code",
            "Filename contains invalid DOW name and/or HA cipher",
        ]
    }

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert exc.value.args[0] == expected


@freeze_time("2020-02-01")
def test_validate_filename_all_invalid_raises_InvalidFilename():
    filename = "AZ2023_GAR4BRF1.ZZZ"

    expected = {
        "message": [
            "Filename contains invalid practice code",
            "Filename contains invalid DOW name and/or HA cipher",
            "Filename contains invalid extension",
        ]
    }

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert exc.value.args[0] == expected


@freeze_time("2020-02-01")
def test_validate_filename_no_filename_regex_match_raises_InvalidFilename():
    filename = "A82023_GDR4BRF1.B1A"

    expected = {"message": ["Filename contains invalid DOW name and/or HA cipher"]}

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert exc.value.args[0] == expected


@freeze_time("2020-02-01")
def test_validate_filename_no_extension_regex_match_raises_InvalidFilename():
    filename = "A82023_GPR4BRF1.B19"

    expected = {"message": ["Filename contains invalid extension"]}

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert exc.value.args[0] == expected


@freeze_time("2020-03-01")
def test_validate_filename_old_filedate_raises_InvalidFilename():
    filename = "A82023_GPR4BRF1.B1A"

    expected = {"message": ["File date must not be older than 14 days"]}

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert exc.value.args[0] == expected


@freeze_time("2020-02-01")
def test_validate_filename_future_filedate_raises_InvalidFilename():
    filename = "A82023_GPR4BRF1.C1A"

    expected = {"message": ["File date must not be from the future"]}

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert exc.value.args[0] == expected


@freeze_time("2020-02-05")
def test_validate_filename_valid_month_indicator_parses_date_correctly():
    valid_month_indicator = "B"

    filename = f"A82023_GPR4BRF1.{valid_month_indicator}5A"

    expected = {
        "filename": "A82023_GPR4BRF1.B5A",
        "extract_date": datetime.now(),
        "practice_code": "A82023",
        "ha_cipher": "BRF",
    }

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-12-15")
def test_validate_filename_valid_day_indicator_parses_date_correctly():
    valid_day_indicator = "F"

    filename = f"A82023_GPR4BRF1.L{valid_day_indicator}A"

    expected = {
        "filename": "A82023_GPR4BRF1.LFA",
        "extract_date": datetime.now(),
        "practice_code": "A82023",
        "ha_cipher": "BRF",
    }

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-02-25")
def test_validate_filename_invalid_date_indicator_raises_ValueError():
    # BV = February 31
    invalid_date_indicator = "BV"

    filename = f"A82023_GPR4BRF1.{invalid_date_indicator[0]}{invalid_date_indicator[1]}A"

    expected = {"message": ["Filename contains invalid date"]}

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert exc.value.args[0] == expected


@freeze_time("2020-01-01")
def test_validate_filename_new_year_start_indicator_returns_valid():
    # LI = December 18
    filename = "A82023_GPR4BRF1.LIA.dat"

    expected = {
        "filename": "A82023_GPR4BRF1.LIA",
        "extract_date": datetime(2019, 12, 18),
        "practice_code": "A82023",
        "ha_cipher": "BRF",
    }

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020-01-14")
def test_validate_filename_new_year_limit_indicator_returns_valid():
    # LV = December 31
    filename = "A82023_GPR4BRF1.LVA.dat"

    expected = {
        "filename": "A82023_GPR4BRF1.LVA",
        "extract_date": datetime(2019, 12, 31),
        "practice_code": "A82023",
        "ha_cipher": "BRF",
    }

    actual = validate_filename(filename)

    assert expected == actual


@freeze_time("2020, 01, 15")
def test_validate_filename_exceed_new_year_limit_raises_InvalidFilename():
    # LV = December 31
    filename = "A82023_GPR4BRF1.LVA"

    expected = {"message": ["File date must not be from the future"]}

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert exc.value.args[0] == expected


@freeze_time("2019, 12, 31")
def test_validate_filename_future_new_year_indicator_raises_InvalidFilename():
    # A1 = January 1
    filename = "A82023_GPR4BRF1.A1A"

    expected = {"message": ["File date must not be older than 14 days"]}

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)

    assert exc.value.args[0] == expected


@freeze_time("2020-02-01")
def test_validate_filename_invalid_chars_as_dat_raises_InvalidFilename():
    filename = "A82023_GPR4BRF1.B1B.d@t"

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)


@freeze_time("2020-02-01")
def test_validate_filename_invalid_backwards_dat_raises_InvalidFilename():
    filename = "A82023_GPR4BRF1.B1B.tad"

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)


@freeze_time("2020-02-01")
def test_validate_filename_invalid_garbled_dat_raises_InvalidFilename():
    filename = "A82023_GPR4BRF1.B1B.Daaaat"

    with pytest.raises(InvalidFilename) as exc:
        validate_filename(filename)
