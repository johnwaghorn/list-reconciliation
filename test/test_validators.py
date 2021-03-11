from datetime import datetime
import pytest

from listrec.parser import validators as v
from listrec.parser.parser import _validate_record


@pytest.mark.parametrize(
    "val,expected",
    (
        ("DOW", ("DOW", None)),
        ("DOWNLOAD", ("DOWNLOAD", v.INVALID_RECORD_TYPE)),
        ("Not", ("Not", v.INVALID_RECORD_TYPE)),
        (" ", (" ", v.INVALID_RECORD_TYPE)),
        ("", (None, v.INVALID_NULL)),
        (None, (None, v.INVALID_NULL)),
        ("Dow", ("Dow", v.INVALID_RECORD_TYPE)),
        (0, (0, v.INVALID_RECORD_TYPE)),
    ),
)
def test_record_type_validator_return_values(val, expected):
    actual = v.VALIDATORS[v.RECORD_TYPE_COL](val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("1234567,123ABC", ("1234567,123ABC", None)),
        ("1234567,1", ("1234567,1", None)),
        ("1234567,A", ("1234567,A", None)),
        ("1234567.123ABC", ("1234567.123ABC", v.INVALID_GP_CODE)),
        ("123456723ABC", ("123456723ABC", v.INVALID_GP_CODE)),
        ("1234567,1234567", ("1234567,1234567", v.INVALID_GP_CODE)),
        ("1234567,", ("1234567,", v.INVALID_GP_CODE)),
        ("123456,123456", ("123456,123456", v.INVALID_GP_CODE)),
        ("123456B,123456", ("123456B,123456", v.INVALID_GP_CODE)),
        (" ", (" ", v.INVALID_GP_CODE)),
        ("", (None, v.INVALID_NULL)),
        (None, (None, v.INVALID_NULL)),
    ),
)
def test_gp_code_validator_return_values(val, expected):
    actual = v.VALIDATORS[v.GP_CODE_COL](val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("1234567890", ("1234567890", None)),
        ("ABC1234?/012345", ("ABC1234?/012345", None)),
        ("", (None, None)),
        (None, (None, None)),
        ("JRDAN 123", ("JRDAN 123", v.INVALID_NHS_NO)),
        ("ABC1234[+012345", ("ABC1234[+012345", v.INVALID_NHS_NO)),
        (" ", (" ", v.INVALID_NHS_NO)),
        (1, (1, v.INVALID_NHS_NO)),
        ("ABC", ("ABC", None)),
    ),
)
def test_nhs_number_validator_return_values(val, expected):
    actual = v.VALIDATORS[v.NHS_NUMBER_COL](val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("", (None, None)),
        (None, (None, None)),
        ("SMITH", ("SMITH", None)),
        ("O'CONNOR", ("O'CONNOR", None)),
        ("SMITH" * 7, ("SMITH" * 7, None)),
        ("'- ", ("'- ", None)),
        ("SMITH" * 7 + "Y", ("SMITH" * 7 + "Y", v.INVALID_SURNAME)),
        ("Smith", ("Smith", v.INVALID_SURNAME)),
        (1, (1, v.INVALID_SURNAME)),
        (" ", (" ", None)),
    ),
)
def test_surname_validator_return_values(val, expected):
    actual = v.VALIDATORS[v.SURNAME_COL](val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("", (None, None)),
        (None, (None, None)),
        ("SMITH", ("SMITH", None)),
        ("O'CONNOR", ("O'CONNOR", None)),
        ("SMITH" * 7, ("SMITH" * 7, None)),
        ("'- ,.", ("'- ,.", None)),
        ("SMITH" * 7 + "Y", ("SMITH" * 7 + "Y", None)),
        ("JOHN O'CONNOR", ("JOHN O'CONNOR", None)),
        ("JOHN O-CONNOR", ("JOHN O-CONNOR", None)),
        ("PETER " + ("SMITH" * 7) + "EXTRA", ("PETER "+ ("SMITH" * 7)+ "EXTRA", None)),
        ("Smith", ("Smith", v.INVALID_FORENAME)),
        (1, (1, v.INVALID_FORENAME)),
        (" ", (" ", v.INVALID_FORENAME)),
    ),
)
def test_forename_validator_return_values(val, expected):
    actual = v.VALIDATORS[v.FORENAMES_COL](val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("", (None, None)),
        (None, (None, None)),
        ("SMITH", ("SMITH", None)),
        ("O'CONNOR", ("O'CONNOR", None)),
        ("SMITH" * 7, ("SMITH" * 7, None)),
        ("'- ", ("'- ", None)),
        ("SMITH" * 7 + "Y", ("SMITH" * 7 + "Y", v.INVALID_TITLE)),
        ("Smith", ("Smith", v.INVALID_TITLE)),
        (1, (1, v.INVALID_TITLE)),
        (" ", (" ", None)),
    ),
)
def test_title_validator_return_values(val, expected):
    actual = v.VALIDATORS[v.TITLE_COL](val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("1", (1, None)),
        ("2", (2, None)),
        ("0", (0, None)),
        ("9", (9, None)),
        ("", (None, None)),
        (None, (None, None)),
        ("3", ("3", v.INVALID_SEX)),
        ("A", ("A", v.INVALID_SEX)),
        (" ", (" ", v.INVALID_SEX)),
        ([], ([], v.INVALID_SEX)),
    ),
)
def test_sex_validator_return_values(val, expected):
    actual = v.VALIDATORS[v.SEX_COL](val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("20120105", (datetime(2012, 1, 5).date(), None)),
        ("", (None, None)),
        (None, (None, None)),
        ("2012015", ("2012015", v.INVALID_DATE_OF_BIRTH)),
        ("25", ("25", v.INVALID_DATE_OF_BIRTH)),
        ("21500105", (datetime(2150, 1, 5).date(), v.INVALID_DATE_OF_BIRTH)),
        (" ", (" ", v.INVALID_DATE_OF_BIRTH)),
        (1, (1, v.INVALID_DATE_OF_BIRTH)),
    ),
)
def test_dob_validator_return_values(val, expected):
    actual = v.VALIDATORS[v.DOB_COL](val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("", (None, None)),
        (None, (None, None)),
        ("SMITH123", ("SMITH123", None)),
        ("O'CONNOR123", ("O'CONNOR123", None)),
        ("SMIT1" * 7, ("SMIT1" * 7, None)),
        ("'- ", ("'- ", None)),
        ("SMITH" * 7 + "Y", ("SMITH" * 7 + "Y", v.INVALID_ADDRESS_LINE)),
        ("Smith", ("Smith", v.INVALID_ADDRESS_LINE)),
        (" ", (" ", None)),
        (1, (1, v.INVALID_ADDRESS_LINE)),
    ),
)
def test_address_line_validator_return_values(val, expected):
    actual = v.VALIDATORS[v.ADDRESS_LINE1_COL](val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("", (None, None)),
        (None, (None, None)),
        ("HP15 6QX", ("HP15 6QX", None)),
        ("HP8 6QX", ("HP8 6QX", None)),
        ("HP15 6QX", ("HP15 6QX", None)),
        ("HP   6QX", ("HP   6QX", None)),
        ("HP156QX", ("HP156QX", v.INVALID_POSTCODE)),
        ("HP D  QX", ("HP D  QX", v.INVALID_POSTCODE)),
        (" ", (" ", v.INVALID_POSTCODE)),
        (1, (1, v.INVALID_POSTCODE)),
    ),
)
def test_postcode_validator_return_values(val, expected):
    actual = v.VALIDATORS[v.POSTCODE_COL](val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("", (None, None)),
        (None, (None, None)),
        ("Y", ("Y", None)),
        ("N", ("N", v.INVALID_DRUGS_DISPENSED_MARKER)),
        (" ", (" ", v.INVALID_DRUGS_DISPENSED_MARKER)),
    ),
)
def test_drugs_dispensed_marker_validator_return_values(val, expected):
    actual = v.VALIDATORS[v.DRUGS_DISPENSED_MARKER](val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("", (None, None)),
        (None, (None, None)),
        ("3", (3, None)),
        ("50", (50, None)),
        ("2", (2, v.INVALID_RPP_MILEAGE)),
        ("51", (51, v.INVALID_RPP_MILEAGE)),
        (" ", (" ", v.INVALID_RPP_MILEAGE)),
        ([], ([], v.INVALID_RPP_MILEAGE)),
    ),
)
def test_rpp_mileage_validator_return_values(val, expected):
    actual = v.VALIDATORS[v.RPP_MILEAGE](val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("", (None, None)),
        (None, (None, None)),
        ("B", ("B", None)),
        ("S", ("S", None)),
        ("A", ("A", v.INVALID_BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER)),
        (" ", (" ", v.INVALID_BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER)),
        (1, (1, v.INVALID_BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER)),
    ),
)
def test_blocked_route_special_district_marker_validator_return_values(val, expected):
    actual = v.VALIDATORS[v.BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER](val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("", (None, None)),
        (None, (None, None)),
        ("3", (3, None)),
        ("99", (99, None)),
        ("2", (2, v.INVALID_WALKING_UNITS)),
        ("100", (100, v.INVALID_WALKING_UNITS)),
        ([], ([], v.INVALID_WALKING_UNITS)),
    ),
)
def test_walking_units_validator_return_values(val, expected):
    actual = v.VALIDATORS[v.WALKING_UNITS](val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("", (None, None)),
        (None, (None, None)),
        ("A1", ("A1", None)),
        ("AA", ("AA", None)),
        ("11", ("11", None)),
        ("A", ("A", v.INVALID_RESIDENTIAL_INSTITUTE_CODE)),
        ("1", ("1", v.INVALID_RESIDENTIAL_INSTITUTE_CODE)),
        ("A11", ("A11", v.INVALID_RESIDENTIAL_INSTITUTE_CODE)),
        ("AAA", ("AAA", v.INVALID_RESIDENTIAL_INSTITUTE_CODE)),
        ([], ([], v.INVALID_RESIDENTIAL_INSTITUTE_CODE)),
    ),
)
def test_residential_institute_code_validator_return_values(val, expected):
    actual = v.VALIDATORS[v.RESIDENTIAL_INSTITUTE_CODE](val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,process_datetime,expected",
    (
        (
            "201206060101",
            datetime(2012, 6, 20, 1, 1),
            (datetime(2012, 6, 6, 1, 1), None),
        ),
        (
            "201206060101",
            datetime(2012, 6, 20, 1, 1, 1),
            (datetime(2012, 6, 6, 1, 1), v.INVALID_TRANS_DATETIME),
        ),
        (
            "2012060601",
            datetime(2012, 6, 20, 1, 1, 1),
            ("2012060601", v.INVALID_TRANS_DATETIME),
        ),
        (
            "000000000000",
            datetime(2012, 6, 20, 1, 1, 1),
            ("000000000000", v.INVALID_TRANS_DATETIME),
        ),
    ),
)
def test_transaction_datetime_validators_return_values(val, process_datetime, expected):
    assert v.VALIDATORS[v.TRANS_DATETIME_COL](val, process_datetime) == expected


@pytest.mark.parametrize(
    "val,gp_ha_cipher,expected",
    (
        ("LA0", "LA0", ("LA0", None)),
        ("111", "111", ("111", None)),
        ("AAA", "AAA", ("AAA", None)),
        ("LA0", "LA0", ("LA0", None)),
        ("", "", (None, v.INVALID_NULL)),
        (None, "LA0", (None, v.INVALID_NULL)),
        ("A", "A", ("A", v.INVALID_HA_CIPHER)),
        ("1", "1", ("1", v.INVALID_HA_CIPHER)),
        ("LA0A", "LA0A", ("LA0A", v.INVALID_HA_CIPHER)),
        ("1111", "1111", ("1111", v.INVALID_HA_CIPHER)),
        ("LA0", "LA1", ("LA0", v.INVALID_HA_CIPHER)),
    ),
)
def test_ha_cipher_validators_return_values(val, gp_ha_cipher, expected):
    assert v.VALIDATORS[v.HA_CIPHER_COL](val, gp_ha_cipher) == expected


def test_validate_record_contains_invalid_dict():
    assert _validate_record({"RECORD_TYPE": "Not"}, datetime.now()) == {
        "RECORD_TYPE": "Not",
        "_INVALID_": {"RECORD_TYPE": v.INVALID_RECORD_TYPE},
    }


@pytest.mark.parametrize(
    "val,expected",
    (
        ("", (None, v.INVALID_NULL)),
        (None, (None, v.INVALID_NULL)),
        ("A1", ("A1", None)),
        (" ", (" ", None)),
    ),
)
def test_not_null_decorator_return_values(val, expected):
    @v.not_null
    def dummy(val):
        return val, None

    actual = dummy(val)

    assert actual == expected


@pytest.mark.parametrize(
    "val,ids,expected",
    (
        ("1", [], (1, None)),
        (1, [], (1, None)),
        ("123", [], (123, None)),
        ("", [], (None, v.INVALID_NULL)),
        (None, [], (None, v.INVALID_NULL)),
        (" ", [], (" ", v.INVALID_TRANS_ID)),
        ("0", [], ("0", v.INVALID_TRANS_ID)),
        ("-1", [], ("-1", v.INVALID_TRANS_ID)),
        ("1.5", [], ("1.5", v.INVALID_TRANS_ID)),
        (1.5, [], (1.5, v.INVALID_TRANS_ID)),
        ("0123", [], ("0123", v.INVALID_TRANS_ID)),
        ("A", [], ("A", v.INVALID_TRANS_ID)),
        ("1", [2, 3, 4], (1, None)),
        ("1", [1, 2, 3, 4], (1, v.INVALID_TRANS_ID)),
    ),
)
def test_transaction_id_validators_return_values(val, ids, expected):
    assert v.VALIDATORS[v.TRANS_ID_COL](val, ids) == expected
