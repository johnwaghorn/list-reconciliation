import os
from datetime import datetime

import pytest
from freezegun import freeze_time
from gp_file_parser.parser import (
    _validate_columns,
    output_records,
    parse_gp_extract_file,
    parse_gp_extract_text,
    process_invalid_records,
)
from lr_logging.exceptions import InvalidGPExtract, InvalidStructure

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "..", "_data", "gp_file_parser")


def test_parse_gp_extract_text_parses_correctly():
    text = (
        "503\\*\n\nDOW~1~1111111,1234~LNA~20200406~1340~1557490~"
        "1234567890~SOMEBODY~JOHN~SOMEONE~MR~1~20020101~FLAT A~THE STREET"
        "\n\nDOW~2~~EAST~~E1   1AA~~3~~~  \n\nDOW~1~1111112,1235~LNA~20200406"
        "~1340~1557491~1234567891~SOMEBODY~JANE~FOE~MISS~1~20120211~FLAT B~"
        "THE STREET\n\nDOW~2~~EAST~~E1   1AA~~3~~~"
    )

    expected = [
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557490,
            "NHS_NUMBER": "1234567890",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "JOHN",
            "PREV_SURNAME": "SOMEONE",
            "TITLE": "MR",
            "SEX": 1,
            "DOB": "2002-01-01",
            "ADDRESS_LINE1": "FLAT A",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
        },
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111112,1235",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557491,
            "NHS_NUMBER": "1234567891",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "JANE",
            "PREV_SURNAME": "FOE",
            "TITLE": "MISS",
            "SEX": 1,
            "DOB": "2012-02-11",
            "ADDRESS_LINE1": "FLAT B",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
        },
    ]

    actual = parse_gp_extract_text(
        text,
        process_datetime=datetime(2020, 4, 6, 13, 40),
        gp_ha_cipher="LNA",
    )

    assert actual == expected


def test_parse_gp_extract_text_with_junk_parses_correctly():
    text = (
        "503\\*\n\nDOW~1~1111111,1234~LNA~20200406~1340~1557490~"
        "1234567890~SOMEBODY~JOHN~SOMEONE~MR~1~20020101~FLAT A~THE STREET"
        "\n\nDOW~2~~EAST~~E1   1AA~~3~~~  \n\nDOW~1~1111111,1234~LNA~20200406"
        "~1340~1557491~1234567891~SOMEBODY~JANE~FOE~MISS~1~20120211~FLAT B~"
        "THE STREET\n\nDOW~2~~EAST~~E1   1AA~~3~~~   \n***\n**\n*\n\n\n"
    )

    expected = [
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557490,
            "NHS_NUMBER": "1234567890",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "JOHN",
            "PREV_SURNAME": "SOMEONE",
            "TITLE": "MR",
            "SEX": 1,
            "DOB": "2002-01-01",
            "ADDRESS_LINE1": "FLAT A",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
        },
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557491,
            "NHS_NUMBER": "1234567891",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "JANE",
            "PREV_SURNAME": "FOE",
            "TITLE": "MISS",
            "SEX": 1,
            "DOB": "2012-02-11",
            "ADDRESS_LINE1": "FLAT B",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
        },
    ]

    actual = parse_gp_extract_text(
        text,
        process_datetime=datetime(2020, 4, 6, 13, 40),
        gp_ha_cipher="LNA",
    )

    assert actual == expected


def test_parse_gp_extract_text_no_valid_records_raises_InvalidStructure():
    text = "503\\*\n\n***\n**\n*\n\n***\n**\n*\n\n"
    with pytest.raises(InvalidStructure):
        parse_gp_extract_text(
            text,
            process_datetime=datetime(2020, 4, 6, 13, 40),
            gp_ha_cipher="LNA",
        )


def test_parse_gp_extract_text_with_columns_parses_correctly():
    text = (
        "503\\*\n\nDOW~1~REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE~"
        "TRADING_PARTNER_NHAIS_CIPHER~DATE_OF_DOWNLOAD~TIME_OF_DOWNLOAD~"
        "TRANS_ID~NHS_NUMBER~SURNAME~FORENAMES~PREV_SURNAME~"
        "TITLE~SEX~DOB~ADDRESS_LINE1~ADDRESS_LINE2\n\n"
        "DOW~2~ADDRESS_LINE3~ADDRESS_LINE4~ADDRESS_LINE5~POSTCODE~~"
        "RPP_MILEAGE~~~  \n\nDOW~1~1111111,1234~LNA~20200406~1340~1557490~"
        "1234567890~SOMEBODY~JOHN~SOMEONE~MR~1~20020101~FLAT A~THE STREET"
        "\n\nDOW~2~~EAST~~E1   1AA~~3~~~  \n\nDOW~1~1111111,1234~LNA~20200406"
        "~1340~1557491~1234567891~SOMEBODY~JANE~FOE~MISS~1~20120211~FLAT B~"
        "THE STREET\n\nDOW~2~~EAST~~E1   1AA~~3~~~   "
    )

    expected = [
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557490,
            "NHS_NUMBER": "1234567890",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "JOHN",
            "PREV_SURNAME": "SOMEONE",
            "TITLE": "MR",
            "SEX": 1,
            "DOB": "2002-01-01",
            "ADDRESS_LINE1": "FLAT A",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
        },
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557491,
            "NHS_NUMBER": "1234567891",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "JANE",
            "PREV_SURNAME": "FOE",
            "TITLE": "MISS",
            "SEX": 1,
            "DOB": "2012-02-11",
            "ADDRESS_LINE1": "FLAT B",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
        },
    ]

    actual = parse_gp_extract_text(
        text,
        process_datetime=datetime(2020, 4, 6, 13, 40),
        gp_ha_cipher="LNA",
    )

    assert actual == expected


def test_parse_gp_extract_text_with_columns_and_junk_parses_correctly():
    text = (
        "503\\*\n\nDOW~1~REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE~"
        "TRADING_PARTNER_NHAIS_CIPHER~DATE_OF_DOWNLOAD~TIME_OF_DOWNLOAD~"
        "TRANS_ID~NHS_NUMBER~SURNAME~FORENAMES~PREV_SURNAME~"
        "TITLE~SEX~DOB~ADDRESS_LINE1~ADDRESS_LINE2\n\n"
        "DOW~2~ADDRESS_LINE3~ADDRESS_LINE4~ADDRESS_LINE5~POSTCODE~~"
        "RPP_MILEAGE~~~  \n\nDOW~1~1111111,1234~LNA~20200406~1340~1557490~"
        "1234567890~SOMEBODY~JOHN~SOMEONE~MR~1~20020101~FLAT A~THE STREET"
        "\n\nDOW~2~~EAST~~E1   1AA~~3~~~  \n\nDOW~1~1111111,1234~LNA~20200406"
        "~1340~1557491~1234567891~SOMEBODY~JANE~FOE~MISS~1~20120211~FLAT B~"
        "THE STREET\n\nDOW~2~~EAST~~E1   1AA~~3~~~   \n*\n\n\n*\n\n\n*\n**\n*"
    )

    expected = [
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557490,
            "NHS_NUMBER": "1234567890",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "JOHN",
            "PREV_SURNAME": "SOMEONE",
            "TITLE": "MR",
            "SEX": 1,
            "DOB": "2002-01-01",
            "ADDRESS_LINE1": "FLAT A",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
        },
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557491,
            "NHS_NUMBER": "1234567891",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "JANE",
            "PREV_SURNAME": "FOE",
            "TITLE": "MISS",
            "SEX": 1,
            "DOB": "2012-02-11",
            "ADDRESS_LINE1": "FLAT B",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
        },
    ]

    actual = parse_gp_extract_text(
        text,
        process_datetime=datetime(2020, 4, 6, 13, 40),
        gp_ha_cipher="LNA",
    )

    assert actual == expected


@pytest.mark.parametrize("header", ["", "502\\*", "503*", "503"])
def test_parse_gp_extract_text_garbled_503_raises_InvalidStructure(header):
    text = (
        header + "DOW~1~1111111,1234~LNA~20200406~1340~155749~"
        "1234567890~SOMEBODY~JOHN~SOMEONE~MR~1~20020101~FLAT A~THE STREET"
        "\n\nDOW~2~~EAST~~E1   1AA~~3~~~  \n\nDOW~1~1111111,1234~LNA~20200406"
        "~1340~155749~1234567891~SOMEBODY~JANE~FOE~MISS~1~20120211~FLAT B~"
        "THE STREET\n\nDOW~2~~EAST~~E1   1AA~~3~~~   "
    )

    with pytest.raises(InvalidStructure):
        parse_gp_extract_text(text)


@pytest.mark.parametrize("record_type", ["", "NOT"])
def test_parse_gp_extract_text_garbled_record_type1_returns_records(record_type):
    text = (
        f"503\\*\n\n{record_type}~1~1111111,1234~LNA~20200406~1340~155749~"
        "1234567890~SOMEBODY~JOHN~SOMEONE~MR~1~20020101~FLAT A~THE STREET"
        "\n\nDOW~2~~EAST~~E1   1AA~~3~~~\n"
    )

    expected = [
        {
            "ADDRESS_LINE1": "FLAT A",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "DOB": "2002-01-01",
            "DRUGS_DISPENSED_MARKER": None,
            "FORENAMES": "JOHN",
            "NHS_NUMBER": "1234567890",
            "POSTCODE": "E1   1AA",
            "PREV_SURNAME": "SOMEONE",
            "RECORD_TYPE_1": None,
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "RESIDENTIAL_INSTITUTE_CODE": None,
            "RPP_MILEAGE": 3,
            "SEX": 1,
            "SURNAME": "SOMEBODY",
            "TITLE": "MR",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "TRANS_ID": 155749,
            "WALKING_UNITS": None,
            "_INVALID_": {
                "ON_LINES": "2-3",
                "RECORD_TYPE_1": "Transaction/Record Type - Row 1 of record must be 'DOW~1'.",
            },
        }
    ]

    actual = parse_gp_extract_text(
        text,
        process_datetime=datetime(2020, 4, 6, 13, 40),
        gp_ha_cipher="LNA",
    )

    assert actual == expected


@pytest.mark.parametrize("record_type", ["", "NOT"])
def test_parse_gp_extract_text_garbled_record_type2_returns_records(record_type):
    text = (
        "503\\*\n\nDOW~1~1111111,1234~LNA~20200406~1340~155749~"
        "1234567890~SOMEBODY~JOHN~SOMEONE~MR~1~20020101~FLAT A~THE STREET"
        f"\n\n{record_type}~2~~EAST~~E1   1AA~~3~~~\n"
    )

    expected = [
        {
            "ADDRESS_LINE1": "FLAT A",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "DOB": "2002-01-01",
            "DRUGS_DISPENSED_MARKER": None,
            "FORENAMES": "JOHN",
            "NHS_NUMBER": "1234567890",
            "POSTCODE": "E1   1AA",
            "PREV_SURNAME": "SOMEONE",
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": None,
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "RESIDENTIAL_INSTITUTE_CODE": None,
            "RPP_MILEAGE": 3,
            "SEX": 1,
            "SURNAME": "SOMEBODY",
            "TITLE": "MR",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "TRANS_ID": 155749,
            "WALKING_UNITS": None,
            "_INVALID_": {
                "ON_LINES": "2-3",
                "RECORD_TYPE_2": "Transaction/Record Type - Row 2 of record must be 'DOW~2'.",
            },
        }
    ]

    actual = parse_gp_extract_text(
        text,
        process_datetime=datetime(2020, 4, 6, 13, 40),
        gp_ha_cipher="LNA",
    )

    assert actual == expected


@freeze_time("2020-04-08")
def test_parse_gp_extract_file_parses_correctly():
    filename = "A82023_GPR4LNA1.CSA"
    file_path = os.path.join(DATA, filename)
    expected = [
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557492,
            "NHS_NUMBER": "1234567890",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "JOHN",
            "PREV_SURNAME": "SOMEONE",
            "TITLE": "MR",
            "SEX": 1,
            "DOB": "2002-01-01",
            "ADDRESS_LINE1": "FLAT A",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
        },
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557493,
            "NHS_NUMBER": "1234567891",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "JANE",
            "PREV_SURNAME": "FOE",
            "TITLE": "MISS",
            "SEX": 1,
            "DOB": "2012-02-11",
            "ADDRESS_LINE1": "FLAT B",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
        },
    ]

    actual = parse_gp_extract_file(
        file_path,
        process_datetime=datetime(2020, 4, 6, 13, 40),
    )

    assert actual == expected


@pytest.mark.parametrize(
    "row_cols,expect_raise",
    (
        ([("col1", "val1")], False),
        ([("col1", "")], False),
        ([("", "")], False),
        ([("", "val1")], InvalidGPExtract),
    ),
)
def test_validate_columns_raises_assertion_error(row_cols, expect_raise):
    if expect_raise:
        with pytest.raises(expect_raise) as err:
            _validate_columns(row_cols)

            expected = {
                "INVALID_RECORD": "Record contains invalid data/structure, and could not be read"
            }

            actual = err.args[0]

            assert expected == actual

    else:
        _validate_columns(row_cols)


@pytest.fixture
def records():
    return [
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557491,
            "NHS_NUMBER": "8234567890",
            "SURNAME": "PHILIP",
            "FORENAMES": "JOHN",
            "PREV_SURNAME": "SOMEONE",
            "TITLE": "MR",
            "SEX": 10,
            "DOB": "2002-01-01",
            "ADDRESS_LINE1": "FLAT 1",
            "ADDRESS_LINE2": "MAIN STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
            "_INVALID_": {
                "SEX": "must be 1 for Male, 2 for Female, 0 "
                "for Indeterminate/Not Known or 9 for Not Specified."
            },
        },
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LONG",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557492,
            "NHS_NUMBER": "9234567890",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "SAM",
            "PREV_SURNAME": "FOE",
            "TITLE": "MS",
            "SEX": 5,
            "DOB": "2012-02-11",
            "ADDRESS_LINE1": "12",
            "ADDRESS_LINE2": "LONG STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
            "_INVALID_": {
                "SEX": "must be 1 for Male, 2 for Female, 0 "
                "for Indeterminate/Not Known or 9 for Not Specified.",
                "TRADING_PARTNER_NHAIS_CIPHER": "must be a 3-digit alphanumeric code and match the GP HA cipher",
            },
        },
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557493,
            "NHS_NUMBER": "8234567890",
            "SURNAME": "PHILIP",
            "FORENAMES": "JOHN",
            "PREV_SURNAME": "SOMEONE",
            "TITLE": "MR",
            "SEX": 1,
            "DOB": "2002-01-01",
            "ADDRESS_LINE1": "FLAT 1",
            "ADDRESS_LINE2": "MAIN STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
        },
    ]


@pytest.fixture
def expected_count_dict():
    return {
        "RECORD_TYPE_1": 0,
        "RECORD_TYPE_2": 0,
        "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": 0,
        "TRADING_PARTNER_NHAIS_CIPHER": 1,
        "DATE_OF_DOWNLOAD": 0,
        "TRANS_ID": 0,
        "NHS_NUMBER": 0,
        "SURNAME": 0,
        "FORENAMES": 0,
        "PREV_SURNAME": 0,
        "TITLE": 0,
        "SEX": 2,
        "DOB": 0,
        "ADDRESS_LINE1": 0,
        "ADDRESS_LINE2": 0,
        "ADDRESS_LINE3": 0,
        "ADDRESS_LINE4": 0,
        "ADDRESS_LINE5": 0,
        "POSTCODE": 0,
        "DRUGS_DISPENSED_MARKER": 0,
        "RPP_MILEAGE": 0,
        "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": 0,
        "WALKING_UNITS": 0,
        "RESIDENTIAL_INSTITUTE_CODE": 0,
    }


def test_process_invalid_records_no_invalid_reason_correct(records, expected_count_dict):
    expected_invalid_records = [
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557491,
            "NHS_NUMBER": "8234567890",
            "SURNAME": "PHILIP",
            "FORENAMES": "JOHN",
            "PREV_SURNAME": "SOMEONE",
            "TITLE": "MR",
            "SEX": 10,
            "DOB": "2002-01-01",
            "ADDRESS_LINE1": "FLAT 1",
            "ADDRESS_LINE2": "MAIN STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
            "_INVALID_": {"SEX": "SEX"},
        },
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LONG",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557492,
            "NHS_NUMBER": "9234567890",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "SAM",
            "PREV_SURNAME": "FOE",
            "TITLE": "MS",
            "SEX": 5,
            "DOB": "2012-02-11",
            "ADDRESS_LINE1": "12",
            "ADDRESS_LINE2": "LONG STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
            "_INVALID_": {
                "SEX": "SEX",
                "TRADING_PARTNER_NHAIS_CIPHER": "TRADING_PARTNER_NHAIS_CIPHER",
            },
        },
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557493,
            "NHS_NUMBER": "8234567890",
            "SURNAME": "PHILIP",
            "FORENAMES": "JOHN",
            "PREV_SURNAME": "SOMEONE",
            "TITLE": "MR",
            "SEX": 1,
            "DOB": "2002-01-01",
            "ADDRESS_LINE1": "FLAT 1",
            "ADDRESS_LINE2": "MAIN STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
        },
    ]

    actual_count, actual_invalid_records = process_invalid_records(records, include_reason=False)

    assert actual_count == expected_count_dict
    assert actual_invalid_records == expected_invalid_records


def test_process_invalid_records_with_invalid_reason_correct(records, expected_count_dict):
    expected_invalid_records = [
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557491,
            "NHS_NUMBER": "8234567890",
            "SURNAME": "PHILIP",
            "FORENAMES": "JOHN",
            "PREV_SURNAME": "SOMEONE",
            "TITLE": "MR",
            "SEX": 10,
            "DOB": "2002-01-01",
            "ADDRESS_LINE1": "FLAT 1",
            "ADDRESS_LINE2": "MAIN STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
            "_INVALID_": {
                "SEX": "SEX must be 1 for Male, 2 for Female, 0 for Indeterminate/Not Known or 9 for Not Specified."
            },
        },
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LONG",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557492,
            "NHS_NUMBER": "9234567890",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "SAM",
            "PREV_SURNAME": "FOE",
            "TITLE": "MS",
            "SEX": 5,
            "DOB": "2012-02-11",
            "ADDRESS_LINE1": "12",
            "ADDRESS_LINE2": "LONG STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
            "_INVALID_": {
                "SEX": "SEX must be 1 for Male, 2 for Female, 0 for Indeterminate/Not Known or 9 for Not Specified.",
                "TRADING_PARTNER_NHAIS_CIPHER": "TRADING_PARTNER_NHAIS_CIPHER must be a 3-digit alphanumeric code and match the GP HA cipher",
            },
        },
        {
            "RECORD_TYPE_1": "DOW",
            "RECORD_TYPE_2": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": "2020-04-06 13:40:00",
            "TRANS_ID": 1557493,
            "NHS_NUMBER": "8234567890",
            "SURNAME": "PHILIP",
            "FORENAMES": "JOHN",
            "PREV_SURNAME": "SOMEONE",
            "TITLE": "MR",
            "SEX": 1,
            "DOB": "2002-01-01",
            "ADDRESS_LINE1": "FLAT 1",
            "ADDRESS_LINE2": "MAIN STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DRUGS_DISPENSED_MARKER": None,
            "RPP_MILEAGE": 3,
            "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER": None,
            "WALKING_UNITS": None,
            "RESIDENTIAL_INSTITUTE_CODE": None,
        },
    ]

    actual_count, actual_invalid_records = process_invalid_records(records, include_reason=True)

    assert actual_count == expected_count_dict
    assert actual_invalid_records == expected_invalid_records


@pytest.fixture
def expected_counts_csv():
    return (
        "COLUMN,COUNT\n"
        "RECORD_TYPE_1,0\n"
        "RECORD_TYPE_2,0\n"
        '"REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE",0\n'
        "TRADING_PARTNER_NHAIS_CIPHER,1\n"
        "DATE_OF_DOWNLOAD,0\n"
        "TRANS_ID,0\n"
        "NHS_NUMBER,0\n"
        "SURNAME,0\n"
        "FORENAMES,0\n"
        "PREV_SURNAME,0\n"
        "TITLE,0\n"
        "SEX,2\n"
        "DOB,0\n"
        "ADDRESS_LINE1,0\n"
        "ADDRESS_LINE2,0\n"
        "ADDRESS_LINE3,0\n"
        "ADDRESS_LINE4,0\n"
        "ADDRESS_LINE5,0\n"
        "POSTCODE,0\n"
        "DRUGS_DISPENSED_MARKER,0\n"
        "RPP_MILEAGE,0\n"
        "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER,0\n"
        "WALKING_UNITS,0\n"
        "RESIDENTIAL_INSTITUTE_CODE,0\n"
    )


def test_output_invalid_records_no_invalid_reason_correct(tmp_path, records, expected_counts_csv):
    out_file_path = os.path.join(tmp_path, "records.csv")
    output_records(records, summary_path=tmp_path, include_reason=False, invalid_threshold=0)

    expected_out_file = (
        '_INVALID_,RECORD_TYPE_1,"REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE",TRADING_PARTNER_NHAIS_CIPHER,DATE_OF_DOWNLOAD,TRANS_ID,NHS_NUMBER,SURNAME,FORENAMES,PREV_SURNAME,TITLE,SEX,DOB,ADDRESS_LINE1,ADDRESS_LINE2,RECORD_TYPE_2,ADDRESS_LINE3,ADDRESS_LINE4,ADDRESS_LINE5,POSTCODE,DRUGS_DISPENSED_MARKER,RPP_MILEAGE,BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER,WALKING_UNITS,RESIDENTIAL_INSTITUTE_CODE\n'
        'SEX,DOW,"1111111,1234",LNA,2020-04-06 '
        "13:40:00,1557491,8234567890,PHILIP,JOHN,SOMEONE,MR,10,2002-01-01,FLAT 1,MAIN "
        "STREET,DOW,,EAST,,E1   1AA,,3,,,\n"
        'SEX | TRADING_PARTNER_NHAIS_CIPHER,DOW,"1111111,1234",LONG,2020-04-06 '
        "13:40:00,1557492,9234567890,SOMEBODY,SAM,FOE,MS,5,2012-02-11,12,LONG "
        "STREET,DOW,,EAST,,E1   1AA,,3,,,\n"
    )

    with open(out_file_path) as out_file:
        actual_out_file = out_file.read()

    assert actual_out_file == expected_out_file

    count_path = os.path.join(tmp_path, "invalid_counts.csv")

    with open(count_path) as count_file:
        actual_counts = count_file.read()

    assert actual_counts == expected_counts_csv


def test_output_invalid_records_with_invalid_reason_low_threshold_correct(
    tmp_path, records, expected_counts_csv
):
    out_file_path = os.path.join(tmp_path, "records.csv")
    output_records(records, summary_path=tmp_path, include_reason=True, invalid_threshold=3)
    expected_out_file = (
        '_INVALID_,RECORD_TYPE_1,"REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE",TRADING_PARTNER_NHAIS_CIPHER,DATE_OF_DOWNLOAD,TRANS_ID,NHS_NUMBER,SURNAME,FORENAMES,PREV_SURNAME,TITLE,SEX,DOB,ADDRESS_LINE1,ADDRESS_LINE2,RECORD_TYPE_2,ADDRESS_LINE3,ADDRESS_LINE4,ADDRESS_LINE5,POSTCODE,DRUGS_DISPENSED_MARKER,RPP_MILEAGE,BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER,WALKING_UNITS,RESIDENTIAL_INSTITUTE_CODE\n'
        '"SEX must be 1 for Male, 2 for Female, 0 for Indeterminate/Not Known or 9 '
        'for Not Specified.",DOW,"1111111,1234",LNA,2020-04-06 '
        "13:40:00,1557491,8234567890,PHILIP,JOHN,SOMEONE,MR,10,2002-01-01,FLAT 1,MAIN "
        "STREET,DOW,,EAST,,E1   1AA,,3,,,\n"
        '"SEX must be 1 for Male, 2 for Female, 0 for Indeterminate/Not Known or 9 '
        "for Not Specified. | TRADING_PARTNER_NHAIS_CIPHER must be a 3-digit "
        "alphanumeric code and match the GP HA "
        'cipher",DOW,"1111111,1234",LONG,2020-04-06 '
        "13:40:00,1557492,9234567890,SOMEBODY,SAM,FOE,MS,5,2012-02-11,12,LONG "
        "STREET,DOW,,EAST,,E1   1AA,,3,,,\n"
    )

    with open(out_file_path) as out_file:
        actual_out_file = out_file.read()

    assert actual_out_file == expected_out_file

    count_path = os.path.join(tmp_path, "invalid_counts.csv")

    with open(count_path) as count_file:
        actual_counts = count_file.read()

    assert actual_counts == expected_counts_csv


def test_output_invalid_records_no_invalid_reason_high_threshold_correct(
    tmp_path, records, expected_counts_csv
):
    out_file_path = os.path.join(tmp_path, "records.csv")
    output_records(records, summary_path=tmp_path, include_reason=False, invalid_threshold=4)

    expected_out_file = (
        '_INVALID_,RECORD_TYPE_1,"REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE",TRADING_PARTNER_NHAIS_CIPHER,DATE_OF_DOWNLOAD,TRANS_ID,NHS_NUMBER,SURNAME,FORENAMES,PREV_SURNAME,TITLE,SEX,DOB,ADDRESS_LINE1,ADDRESS_LINE2,RECORD_TYPE_2,ADDRESS_LINE3,ADDRESS_LINE4,ADDRESS_LINE5,POSTCODE,DRUGS_DISPENSED_MARKER,RPP_MILEAGE,BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER,WALKING_UNITS,RESIDENTIAL_INSTITUTE_CODE\n'
        'SEX,DOW,"1111111,1234",LNA,2020-04-06 '
        "13:40:00,1557491,8234567890,PHILIP,JOHN,SOMEONE,MR,10,2002-01-01,FLAT 1,MAIN "
        "STREET,DOW,,EAST,,E1   1AA,,3,,,\n"
        'SEX | TRADING_PARTNER_NHAIS_CIPHER,DOW,"1111111,1234",LONG,2020-04-06 '
        "13:40:00,1557492,9234567890,SOMEBODY,SAM,FOE,MS,5,2012-02-11,12,LONG "
        "STREET,DOW,,EAST,,E1   1AA,,3,,,\n"
        ',DOW,"1111111,1234",LNA,2020-04-06 '
        "13:40:00,1557493,8234567890,PHILIP,JOHN,SOMEONE,MR,1,2002-01-01,FLAT 1,MAIN "
        "STREET,DOW,,EAST,,E1   1AA,,3,,,\n"
    )

    with open(out_file_path) as out_file:
        actual_out_file = out_file.read()

    assert actual_out_file == expected_out_file

    count_path = os.path.join(tmp_path, "invalid_counts.csv")

    with open(count_path) as count_file:
        actual_counts = count_file.read()

    assert actual_counts == expected_counts_csv
