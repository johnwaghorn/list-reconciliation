from datetime import datetime
import os
import pytest

from parser.parser import (
    parse_gp_extract_text,
    InvalidGPExtract,
    _validate_file_group,
    parse_gp_extract_file_group,
    _validate_columns,
)


ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")


def test_parse_gp_extract_text_parses_correctly():
    text = (
        "503\\*\n\nDOW~1~REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE~"
        "TRADING_PARTNER_NHAIS_CIPHER~DATE_OF_DOWNLOAD~PRACTICE_SITE_NUMBER~"
        "CLINCAL_SYSTEM_NUMBER~NHS_NUMBER~SURNAME~FORENAMES~PREV_SURNAME~"
        "TITLE~SEX_(1=MALE,2=FEMALE)~DOB~ADDRESS_LINE1~ADDRESS_LINE2\n\n"
        "DOW~2~ADDRESS_LINE3~ADDRESS_LINE4~ADDRESS_LINE5~POSTCODE~~"
        "DISTANCE~~~  \n\nDOW~1~1111111,1234~LNA~202004061530~1340~155749~"
        "1234567890~SOMEBODY~JOHN~SOMEONE~MR~1~20020101~FLAT A~THE STREET"
        "\n\nDOW~2~~EAST~~E1   1AA~~3~~~  \n\nDOW~1~1111111,1234~LNA~202004061530"
        "~1340~155749~1234567891~SOMEBODY~JANE~FOE~MISS~1~20120211~FLAT B~"
        "THE STREET\n\nDOW~2~~EAST~~E1   1AA~~3~~~   "
    )

    expected = [
        {
            "RECORD_TYPE": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": datetime(2020, 4, 6, 15, 30),
            "PRACTICE_SITE_NUMBER": "1340",
            "CLINCAL_SYSTEM_NUMBER": "155749",
            "NHS_NUMBER": "1234567890",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "JOHN",
            "PREV_SURNAME": "SOMEONE",
            "TITLE": "MR",
            "SEX_(1=MALE,2=FEMALE)": 1,
            "DOB": datetime(2002, 1, 1).date(),
            "ADDRESS_LINE1": "FLAT A",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DISTANCE": "3",
        },
        {
            "RECORD_TYPE": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": datetime(2020, 4, 6, 15, 30),
            "PRACTICE_SITE_NUMBER": "1340",
            "CLINCAL_SYSTEM_NUMBER": "155749",
            "NHS_NUMBER": "1234567891",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "JANE",
            "PREV_SURNAME": "FOE",
            "TITLE": "MISS",
            "SEX_(1=MALE,2=FEMALE)": 1,
            "DOB": datetime(2012, 2, 11).date(),
            "ADDRESS_LINE1": "FLAT B",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DISTANCE": "3",
        },
    ]

    actual = parse_gp_extract_text(
        text, process_datetime=datetime(2020, 4, 6, 15, 30), gp_ha_cipher="LNA"
    )

    assert actual == expected


@pytest.mark.parametrize("header", ["", "502\\*", "503*", "503"])
def test_parse_gp_extract_text_garbled_503_raises_assertionerror(header):
    text = (
        header + "DOW~1~REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE~"
        "TRADING_PARTNER_NHAIS_CIPHER~DATE_OF_DOWNLOAD~PRACTICE_SITE_NUMBER~"
        "CLINCAL_SYSTEM_NUMBER~NHS_NUMBER~SURNAME~FORENAMES~PREV_SURNAME~"
        "TITLE~SEX_(1=MALE,2=FEMALE)~DOB~ADDRESS_LINE1~ADDRESS_LINE2\n\n"
        "DOW~2~ADDRESS_LINE3~ADDRESS_LINE4~ADDRESS_LINE5~POSTCODE~~"
        "DISTANCE~~~  \n\nDOW~1~1111111,1234~LNA~202004061530~1340~155749~"
        "1234567890~SOMEBODY~JOHN~SOMEONE~MR~1~20020101~FLAT A~THE STREET"
        "\n\nDOW~2~~EAST~~E1   1AA~~3~~~  \n\nDOW~1~1111111,1234~LNA~202004061530"
        "~1340~155749~1234567891~SOMEBODY~JANE~FOE~MISS~1~20120211~FLAT B~"
        "THE STREET\n\nDOW~2~~EAST~~E1   1AA~~3~~~   "
    )

    with pytest.raises(AssertionError):
        parse_gp_extract_text(text)


@pytest.mark.parametrize("record_type", ["", "NOT"])
def test_parse_gp_extract_text_garbled_record_type1_raises_assertionerror(record_type):
    text = (
        f"503\\*\n\n{record_type}~REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE~"
        "TRADING_PARTNER_NHAIS_CIPHER~DATE_OF_DOWNLOAD~PRACTICE_SITE_NUMBER~"
        "CLINCAL_SYSTEM_NUMBER~NHS_NUMBER~SURNAME~FORENAMES~PREV_SURNAME~"
        "TITLE~SEX_(1=MALE,2=FEMALE)~DOB~ADDRESS_LINE1~ADDRESS_LINE2\n\n"
        "DOW~2~ADDRESS_LINE3~ADDRESS_LINE4~ADDRESS_LINE5~POSTCODE~~"
        "DISTANCE~~~  \n\nDOW~1~1111111,1234~LNA~20200406~1340~155749~"
        "1234567890~SOMEBODY~JOHN~SOMEONE~MR~1~20020101~FLAT A~THE STREET"
        "\n\nDOW~2~~EAST~~E1 1AA~~3~~~  \n\nDOW~1~1111111,1234~LNA~20200406"
        "~1340~155749~1234567891~SOMEBODY~JANE~FOE~MISS~1~20120211~FLAT B~"
        "THE STREET\n\nDOW~2~~EAST~~E1 1AA~~3~~~   "
    )

    with pytest.raises(AssertionError):
        parse_gp_extract_text(text)


@pytest.mark.parametrize("record_type", ["", "NOT"])
def test_parse_gp_extract_text_garbled_record_type2_raises_assertionerror(record_type):
    text = (
        "503\\*\n\nDOW~1~REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE~"
        "TRADING_PARTNER_NHAIS_CIPHER~DATE_OF_DOWNLOAD~PRACTICE_SITE_NUMBER~"
        "CLINCAL_SYSTEM_NUMBER~NHS_NUMBER~SURNAME~FORENAMES~PREV_SURNAME~"
        "TITLE~SEX_(1=MALE,2=FEMALE)~DOB~ADDRESS_LINE1~ADDRESS_LINE2\n\n"
        f"{record_type}~ADDRESS_LINE3~ADDRESS_LINE4~ADDRESS_LINE5~POSTCODE~~"
        "DISTANCE~~~  \n\nDOW~1~1111111,1234~LNA~20200406~1340~155749~"
        "1234567890~SOMEBODY~JOHN~SOMEONE~MR~1~20020101~FLAT A~THE STREET"
        "\n\nDOW~2~~EAST~~E1 1AA~~3~~~  \n\nDOW~1~1111111,1234~LNA~20200406"
        "~1340~155749~1234567891~SOMEBODY~JANE~FOE~MISS~1~20120211~FLAT B~"
        "THE STREET\n\nDOW~2~~EAST~~E1 1AA~~3~~~   "
    )

    with pytest.raises(AssertionError):
        parse_gp_extract_text(text)


@pytest.mark.parametrize(
    "group,expect_raise",
    [
        (("GPR4LA01.CSA", "GPR4LA01.CSB"), False),
        (("GPR4LA01.CSB", "GPR4LA01.CSA"), False),
        (("GPR4LA01.CSA",), False),
        (("GPR4LA01.CSA", "XPR4LA01.CSB"), InvalidGPExtract),
        (("GPR4LA01.CSA", "GPR4LA01.CXB"), InvalidGPExtract),
        (("GPR4LA01.CSA", "GPR4LA01.CSC"), InvalidGPExtract),
        (("GPR4LA01.CSB", "GPR4LA01.CSC"), InvalidGPExtract),
        (("GPR4LA01.CSB",), InvalidGPExtract),
        (("GPR4LA01.CS",), InvalidGPExtract),
        (("GPR4LA01.CA",), InvalidGPExtract),
        (("GPR4LA01CSA",), InvalidGPExtract),
        (("",), InvalidGPExtract),
        ([], InvalidGPExtract),
        ("GPR4LA01.CSA", InvalidGPExtract),
    ],
)
def test_validate_file_group(group, expect_raise):
    if expect_raise:
        with pytest.raises(expect_raise):
            _validate_file_group(group)
    else:
        _validate_file_group(group)


def test_parse_gp_extract_file_group_parses_correctly():
    files = ("GPEXTRACT.CSA", "GPEXTRACT.CSB")
    file_group = [os.path.join(DATA, f) for f in files]
    expected = [
        {
            "RECORD_TYPE": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": datetime(2020, 4, 6, 15, 30),
            "PRACTICE_SITE_NUMBER": "1340",
            "CLINCAL_SYSTEM_NUMBER": "155749",
            "NHS_NUMBER": "1234567890",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "JOHN",
            "PREV_SURNAME": "SOMEONE",
            "TITLE": "MR",
            "SEX_(1=MALE,2=FEMALE)": 1,
            "DOB": datetime(2002, 1, 1).date(),
            "ADDRESS_LINE1": "FLAT A",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DISTANCE": "3",
        },
        {
            "RECORD_TYPE": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": datetime(2020, 4, 6, 15, 30),
            "PRACTICE_SITE_NUMBER": "1340",
            "CLINCAL_SYSTEM_NUMBER": "155749",
            "NHS_NUMBER": "1234567891",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "JANE",
            "PREV_SURNAME": "FOE",
            "TITLE": "MISS",
            "SEX_(1=MALE,2=FEMALE)": 1,
            "DOB": datetime(2012, 2, 11).date(),
            "ADDRESS_LINE1": "FLAT B",
            "ADDRESS_LINE2": "THE STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DISTANCE": "3",
        },
        {
            "RECORD_TYPE": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": datetime(2020, 4, 6, 15, 30),
            "PRACTICE_SITE_NUMBER": "1340",
            "CLINCAL_SYSTEM_NUMBER": "155749",
            "NHS_NUMBER": "8234567890",
            "SURNAME": "PHILIP",
            "FORENAMES": "JOHN",
            "PREV_SURNAME": "SOMEONE",
            "TITLE": "MR",
            "SEX_(1=MALE,2=FEMALE)": 2,
            "DOB": datetime(2002, 1, 1).date(),
            "ADDRESS_LINE1": "FLAT 1",
            "ADDRESS_LINE2": "MAIN STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DISTANCE": "3",
        },
        {
            "RECORD_TYPE": "DOW",
            "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "1111111,1234",
            "TRADING_PARTNER_NHAIS_CIPHER": "LNA",
            "DATE_OF_DOWNLOAD": datetime(2020, 4, 6, 15, 30),
            "PRACTICE_SITE_NUMBER": "1340",
            "CLINCAL_SYSTEM_NUMBER": "155749",
            "NHS_NUMBER": "9234567890",
            "SURNAME": "SOMEBODY",
            "FORENAMES": "SAM",
            "PREV_SURNAME": "FOE",
            "TITLE": "MS",
            "SEX_(1=MALE,2=FEMALE)": 1,
            "DOB": datetime(2012, 2, 11).date(),
            "ADDRESS_LINE1": "12",
            "ADDRESS_LINE2": "LONG STREET",
            "ADDRESS_LINE3": None,
            "ADDRESS_LINE4": "EAST",
            "ADDRESS_LINE5": None,
            "POSTCODE": "E1   1AA",
            "DISTANCE": "3",
        },
    ]

    actual = parse_gp_extract_file_group(
        file_group,
        process_datetime=datetime(2020, 4, 6, 15, 30),
        gp_ha_cipher="LNA",
    )

    assert actual == expected


@pytest.mark.parametrize(
    "row_cols,expect_raise",
    (
        ([("col1", "val1")], False),
        ([("col1", "")], False),
        ([("", "")], False),
        ([("", "val1")], AssertionError),
    ),
)
def test_validate_columns_raises_assertion_error(row_cols, expect_raise):
    if expect_raise:
        with pytest.raises(expect_raise):
            _validate_columns(row_cols)
    else:
        _validate_columns(row_cols)
