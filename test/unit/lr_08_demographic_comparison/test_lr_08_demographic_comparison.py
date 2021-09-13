import lr_08_demographic_comparison.lr_08_lambda_handler
import pytest
from comparison_engine.schema import ConfigurationError
from database.models import Demographics, DemographicsDifferences
from lr_08_demographic_comparison.lr_08_lambda_handler import DemographicComparison
from moto import mock_dynamodb2


@pytest.fixture(autouse=True)
def lambda_handler():
    app = DemographicComparison()
    return app


@pytest.fixture
def create_dynamodb_tables():
    with mock_dynamodb2():
        Demographics.create_table()
        DemographicsDifferences.create_table()
        yield


@pytest.fixture
def demographics_record(create_dynamodb_tables):
    items = [
        {
            "Id": "50",
            "JobId": "50",
            "NhsNumber": "9000000009",
            "GP_DateOfBirth": "20101025",
            "GP_Gender": "2",
            "GP_GpPracticeCode": "Y123452",
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
            "PDS_GpPracticeCode": "Y123452",
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
            "GP_RegistrationStatus": "Matched",
        },
        {
            "Id": "51",
            "JobId": "50",
            "NhsNumber": "9000000009",
            "GP_DateOfBirth": "20101025",
            "GP_Gender": "2",
            "GP_GpPracticeCode": "Y123452",
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
            "PDS_GpPracticeCode": "Y45678",
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
            "GP_RegistrationStatus": "Partnership Mismatch",
        },
    ]
    for item in items:
        obj = Demographics(item["Id"], item["JobId"], **item)
        obj.save()
    yield


def test_demographics_comparison_ok(demographics_record, lambda_handler):
    lambda_handler.job_id = "50"
    lambda_handler.patient_id = "50"

    lambda_handler.demographic_comparisons()
    result = DemographicsDifferences.scan()
    actual = [record.attribute_values["RuleId"] for record in result]
    expected = ["MN-BR-DB-01", "MN-BR-AD-01"]
    assert sorted(actual) == sorted(expected)


def test_demographics_comparison_not_matched_ok(demographics_record, lambda_handler):
    lambda_handler.job_id = "50"
    lambda_handler.patient_id = "51"

    lambda_handler.demographic_comparisons()
    result = DemographicsDifferences.scan()
    actual = [record.attribute_values.get("RuleId") for record in result]
    expected = []
    assert actual == expected


def test_record_doesnt_exist_raises_DemographicsDoesNotExist(demographics_record, lambda_handler):
    lambda_handler.job_id = "500"
    lambda_handler.patient_id = "500"

    with pytest.raises(Demographics.DoesNotExist):
        lambda_handler.demographic_comparisons()


def test_bad_config_raises_ConfigurationError(demographics_record, lambda_handler):
    lambda_handler.job_id = "50"
    lambda_handler.patient_id = "50"

    lr_08_demographic_comparison.lr_08_lambda_handler.listrec_comparisons = None
    with pytest.raises(ConfigurationError):
        lambda_handler.demographic_comparisons()
