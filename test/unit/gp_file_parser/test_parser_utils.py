import pytest

from gp_file_parser.utils import empty_string


@pytest.mark.parametrize(
    "val,expected",
    (("TEST", "TEST"), (4, "4"), (0, ""), (" ", ""), ("", ""), (None, "")),
)
def test_record_type_validator_return_values(val, expected):
    actual = empty_string(val)

    assert actual == expected
