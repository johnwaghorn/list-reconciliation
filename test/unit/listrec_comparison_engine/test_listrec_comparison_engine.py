import listrec_comparison_engine
from comparison_engine.core import compare_records


def test_compare_records_all_equal():

    left = {
        "NhsNumber": "123",
        "GP_DateOfBirth": "20130522",
        "GP_Forenames": "Peter Piper",
        "GP_Surname": "Smith",
        "GP_Title": "Mr",
        "GP_Gender": "1",
        "GP_AddressLine1": "19 Orchard Way",
        "GP_AddressLine2": None,
        "GP_AddressLine3": "Leeds",
        "GP_AddressLine4": None,
        "GP_AddressLine5": None,
        "GP_PostCode": "LE12 4RT",
    }

    right = {
        "NhsNumber": "123",
        "PDS_DateOfBirth": "2013-05-22",
        "PDS_Forenames": [" Peter ", "Piper"],
        "PDS_Surname": "Smith",
        "PDS_Titles": ["Mr"],
        "PDS_Gender": "male",
        "PDS_Address": ["19 Orchard       Way", "Leeds"],
        "PDS_PostCode": "LE12    4RT",
    }

    expected = []
    actual = compare_records(listrec_comparison_engine, left, right)

    assert actual == expected


def test_compare_records_some_unequal():
    left = {
        "NhsNumber": "123",
        "GP_DateOfBirth": "20150701",
        "GP_Forenames": "Ella",
        "GP_Surname": "Jones",
        "GP_Title": "Mrs",
        "GP_Gender": "9",
        "GP_AddressLine1": "19 Orchard Park",
        "GP_AddressLine2": None,
        "GP_AddressLine3": "Leeds",
        "GP_AddressLine4": None,
        "GP_AddressLine5": None,
        "GP_PostCode": "LE12 4RT",
    }

    right = {
        "NhsNumber": "456",
        "PDS_DateOfBirth": "2014-07-01",
        "PDS_Forenames": ["Elizabeth"],
        "PDS_Surname": "Jacobs",
        "PDS_Titles": ["Miss"],
        "PDS_Gender": "female",
        "PDS_Address": ["19 Orchard Way", "Leeds"],
        "PDS_PostCode": "LE12    4RT",
    }

    expected = {
        "MN-BR-DB-01",
        "MN-BR-FN-01",
        "MN-BR-SN-01",
        "MN-BR-TL-01",
        "MN-BR-SX-01",
        "MN-BR-AD-01",
    }

    actual = set(compare_records(listrec_comparison_engine, left, right))

    assert actual == expected
