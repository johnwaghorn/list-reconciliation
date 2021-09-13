import datetime

import pytest
from comparison_engine.core import comparison, get_decorated_funcs, get_records, module_from_string
from comparison_engine.schema import (
    ConfigurationError,
    DateTimeColumn,
    FloatColumn,
    IntegerColumn,
    LeftRecord,
    RightRecord,
    StringColumn,
)


def test_get_records_one_right_record_allowed_in_object():
    mod = module_from_string(
        "tmp",
        """
        from comparison_engine.schema import RightRecord

        class ARecord(RightRecord):
            pass


        class BRecord(RightRecord):
            pass""",
    )

    with pytest.raises(ConfigurationError) as err:
        get_records(mod)

    assert str(err.value) == "A RightRecord object has already been defined."


def test_get_records_exactly_one_right_record_required_in_object():
    mod = module_from_string(
        "tmp",
        """
        from comparison_engine.schema import LeftRecord

        class ARecord(LeftRecord):
            pass""",
    )

    with pytest.raises(ConfigurationError) as err:
        get_records(mod)

    assert str(err.value) == "Exactly one LeftRecord and RightRecord object must be defined."


def test_get_records_only_one_left_record_allowed_in_object():
    mod = module_from_string(
        "tmp",
        """
        from comparison_engine.schema import LeftRecord

        class ARecord(LeftRecord):
            pass

        class BRecord(LeftRecord):
            pass""",
    )

    with pytest.raises(ConfigurationError) as err:
        get_records(mod)

    assert str(err.value) == "A LeftRecord object has already been defined."


def test_get_records_exactly_one_left_record_required_in_object():
    mod = module_from_string(
        "tmp",
        """
        from comparison_engine.schema import RightRecord

        class ARecord(RightRecord):
            pass""",
    )

    with pytest.raises(ConfigurationError) as err:
        get_records(mod)

    assert str(err.value) == "Exactly one LeftRecord and RightRecord object must be defined."


def test_record_has_exactly_one_primary_key_required():
    class ARecord(LeftRecord):
        pass

    with pytest.raises(ConfigurationError) as err:
        ARecord({})

    assert str(err.value) == "Record must have exactly one primary_key."


def test_record_has_only_one_primary_key():
    class ARecord(LeftRecord):
        ID1 = IntegerColumn("id1", primary_key=True)
        ID2 = IntegerColumn("id2", primary_key=True)

    with pytest.raises(ConfigurationError) as err:
        ARecord({"id1": 1, "id2": 2})

    assert str(err.value) == "Only one primary_key is allowed per record."


def test_record_primary_key():
    class ARecord(RightRecord):
        ID = IntegerColumn("id", primary_key=True)

    assert ARecord({"id": 10}).primary_key == 10


def test_record_data_types():
    class ARecord(LeftRecord):
        ID = IntegerColumn("id", primary_key=True)
        AMOUNT = FloatColumn("amt")
        NAME = StringColumn("name")
        NAME_WITH_DASH = StringColumn("name", format=lambda x: "-".join(x.lower().split()))
        DATE = DateTimeColumn("date")
        US_DATE = DateTimeColumn(
            "us_date", format=lambda x: datetime.datetime.strptime(str(x), "%Y-%d-%m")
        )
        FORMATTED_NAME = StringColumn(
            ["name", "surname"], format=lambda x: ", ".join(x[::-1]).strip()
        )

    record = ARecord(
        {
            "id": 10,
            "amt": 1.2,
            "name": "John Paul",
            "surname": "Smith",
            "us_date": "2021-22-04",
            "date": 20211012,
        }
    )

    assert record[["ID", "AMOUNT"]] == [10, 1.2]
    assert record["NAME"] == "John Paul"
    assert record["NAME_WITH_DASH"] == "john-paul"
    assert record["DATE"] == datetime.datetime(2021, 10, 12)
    assert record["US_DATE"] == datetime.datetime(2021, 4, 22)
    assert record["FORMATTED_NAME"] == "Smith, John Paul"


def test_comparison_function_id_required():
    with pytest.raises(ConfigurationError):

        @comparison
        def simple_compare(left, right):
            return left != right


def test_get_comparison_functions_ok():
    mod = module_from_string(
        "tmp",
        """
        from comparison_engine.core import comparison

        @comparison('abc123')
        def simple_compare(left, right):
            return left != right

        @comparison('abc456')
        def another_compare(left, right):
            return left != right

        def dummy():
            pass""",
    )
    assert get_decorated_funcs(mod, mod.comparison) == [
        (
            "abc456",
            "another_compare",
            mod.another_compare,
        ),
        (
            "abc123",
            "simple_compare",
            mod.simple_compare,
        ),
    ]


def test_get_comparison_functions_unique_ids():
    mod = module_from_string(
        "tmp",
        """
        from comparison_engine.core import comparison

        @comparison('abc123')
        def simple_compare(left, right):
            return left != right

        @comparison('abc123')
        def another_compare(left, right):
            return left != right""",
    )
    with pytest.raises(ConfigurationError):
        get_decorated_funcs(mod, mod.comparison)
