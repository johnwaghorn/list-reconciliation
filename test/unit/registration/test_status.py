import pytest
from registration import get_gp_registration_status


@pytest.mark.parametrize(
    "gp_gppracticecode,pds_record,expected",
    [
        ("Y1234", {"gp_practicecode": "Y1234"}, "Matched"),
        ("Y1234", {"gp_practicecode": "Y5678"}, "Partnership Mismatch"),
        ("Y1234", {"gp_practicecode": None}, "Deducted Patient Match"),
        ("Y1234", None, "Unmatched"),
    ],
)
def test_get_gp_registration_status_ok(gp_gppracticecode, pds_record, expected):
    actual = get_gp_registration_status(gp_gppracticecode, pds_record)

    assert actual == expected
