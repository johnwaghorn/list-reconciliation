from moto import mock_dynamodb2

import pytest

from comparison_engine.schema import ConfigurationError
from lambdas.LR_08_demographic_comparison.demographic_comparison import demographic_comparisons
from utils.models import Demographics, Errors, DemographicsDifferences

import lambdas.LR_08_demographic_comparison.demographic_comparison


@pytest.fixture
def create_dynamodb_tables():
    with mock_dynamodb2():
        Errors.create_table()
        Demographics.create_table()
        DemographicsDifferences.create_table()
        yield


@pytest.fixture
def demographics_record(create_dynamodb_tables):
    item = {
        "Id": "50",
        "JobId": "50",
        "NhsNumber": "9000000009",
        "GP_DateOfBirth": "20101025",
        "GP_Gender": "2",
        "GP_GpCode": "Y123452",
        "GP_Title": "Mrs",
        "GP_Forenames": "Jane",
        "GP_Surname": "Smith",
        "GP_AddressLine1": "1 Trevelyan Square",
        "GP_AddressLine2": "Boar's Head Lane",
        "GP_AddressLine3": "City Centre",
        "GP_AddressLine4": "Leeds",
        "GP_AddressLine5": "West Yorkshire",
        "GP_PostCode": "LS1 6AE",
        "IsComparisonCompleted": False,
        "GP_HaCipher": "TEST",
        "GP_TransactionDate": "2021-01-01",
        "GP_TransactionTime": "01:00:00",
        "GP_TransactionId": "1234",
        "GP_PreviousSurname": "TEST",
        "GP_DrugsDispensedMarker": False,
        "PDS_GpCode": "Y123452",
        "PDS_GpRegisteredDate": "2012-05-22",
        "PDS_Surname": "Smith",
        "PDS_Forenames": ["Jane"],
        "PDS_Titles": ["Mrs"],
        "PDS_Gender": "female",
        "PDS_DateOfBirth": "2010-10-22",
        "PDS_Sensitive": "U",
        "PDS_Address": [
            "1 Trevelyan Square",
            "Boar Lane",
            "City Centre",
            "Leeds",
            "West Yorkshire",
        ],
        "PDS_PostCode": "LS1 6AE",
    }

    obj = Demographics(item["Id"], item["JobId"], **item)
    obj.save()
    yield item


def test_demographics_comparison_ok(demographics_record):
    demographic_comparisons("50", "50")
    result = DemographicsDifferences.scan()
    actual = {record.attribute_values["RuleId"] for record in result}
    expected = {"date_of_birth_not_equal", "address_not_equal"}

    assert actual == expected


def test_record_doesnt_exist_raises_DemographicsDoesNotExist(demographics_record):
    with pytest.raises(Demographics.DoesNotExist):
        demographic_comparisons("500", "500")


def test_bad_config_raises_ConfigurationError(demographics_record):
    lambdas.LR_08_demographic_comparison.demographic_comparison.listrec_comparisons = None
    with pytest.raises(ConfigurationError):
        demographic_comparisons("50", "50")
