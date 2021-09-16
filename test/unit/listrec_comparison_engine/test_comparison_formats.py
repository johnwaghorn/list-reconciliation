import pytest
from listrec_comparison_engine import format


@pytest.mark.parametrize(
    "val,expected",
    (("20120105", "2012-01-05 00:00:00"),),
)
def test_gp_dob(val, expected):
    actual = format.gp_dob(val)
    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (("2013-05-22", "2013-05-22 00:00:00"),),
)
def test_pds_dob(val, expected):
    actual = format.pds_dob(val)
    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("richard worthing", "richard worthing"),
        ("Richard Worthing", "richard worthing"),
        ("Peter PARKER", "peter parker"),
        ("PETER parker glenn", "peter parker glenn"),
    ),
)
def test_to_lower(val, expected):
    actual = format.to_lower(val)
    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        ("2", "female"),
        (2, "female"),
        ("1", "male"),
        ("0", "other"),
        ("9", "unknown"),
    ),
)
def test_gp_gender(val, expected):
    actual = format.gp_gender(val)
    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (
        (
            [
                "19 Orchard Way",
                None,
                "Leeds",
                None,
                None,
            ],
            "19 Orchard Way, Leeds",
        ),
    ),
)
def test_gp_address(val, expected):
    actual = format.gp_address(val)
    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    ((["19 Orchard       Way", "Leeds"], "19 Orchard Way, Leeds"),),
)
def test_pds_address(val, expected):
    actual = format.pds_address(val)
    assert actual == expected


@pytest.mark.parametrize(
    "val,expected",
    (("LOREM", "LOREM"), ("LOREM                   ", "LOREM"), (["IPSUM             "], "IPSUM")),
)
def test_strip_whitespace(val, expected):
    actual = format.strip_whitespace(val)
    assert actual == expected
