import pytest

from utils.registration_status import get_gp_registration_status


@pytest.mark.parametrize(
    "gp_gpcode,pds_record,expected",
    [
        ("Y1234", {"gp_code": "Y1234"}, "Matched"),
        ("Y1234", {"gp_code": "Y5678"}, "Partnership Mismatch"),
        ("Y1234", {"gp_code": None}, "Deducted Patient Match"),
        ("Y1234", None, "Unmatched"),
    ],
)
def test_get_gp_registration_status_ok(gp_gpcode, pds_record, expected):
    actual = get_gp_registration_status(gp_gpcode, pds_record)

    assert actual == expected
