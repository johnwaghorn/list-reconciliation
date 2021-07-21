import os

from utils.database.models import Demographics
from utils.logger import success

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")

REGION_NAME = "eu-west-2"


def test_write_into_table(
    upload_pds_mock_data_to_s3,
    create_LR08_demographic_comparison_lambda,
    create_dynamodb_tables,
    lambda_context,
    lambda_handler,
):

    record = Demographics(
        "50",
        "50",
        NhsNumber="9000000009",
        GP_DateOfBirth="20101025",
        GP_Gender="2",
        GP_GpCode="Y123452",
        GP_Title="Mrs",
        GP_Forenames="Jane",
        GP_Surname="Smith",
        GP_AddressLine1="1 Trevelyan Square",
        GP_AddressLine2="Boar's Head Lane",
        GP_AddressLine3="City Centre",
        GP_AddressLine4="Leeds",
        GP_AddressLine5="West Yorkshire",
        GP_PostCode="LS1 6AE",
        IsComparisonCompleted=False,
        GP_HaCipher="TEST",
        GP_TransactionDate="2021-01-01",
        GP_TransactionTime="01:00:00",
        GP_TransactionId="1234",
        GP_PreviousSurname="TEST",
        GP_DrugsDispensedMarker=False,
    )
    response = lambda_handler.pds_hydrate("50", record)
    expected_response = success(
        "Retrieved PDS data for JobId: 50, PatientId: 50, NhsNumber: 9000000009"
    )

    assert response == expected_response

    actual = Demographics.get("50", "50").attribute_values

    expected = {
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
            "Leeds",
            "West Yorkshire",
        ],
        "PDS_PostCode": "LS1 6AE",
        "GP_RegistrationStatus": "Matched",
        "PDS_Version": "1",
    }

    assert actual == expected


def test_gp_registration_Partnership_Mismatch_in_demographics_table(
    upload_pds_mock_data_to_s3,
    create_dynamodb_tables,
    create_LR08_demographic_comparison_lambda,
    lambda_handler,
):

    record = Demographics(
        Id="51",
        JobId="50",
        NhsNumber="8000000008",
        GP_DateOfBirth="20091022",
        GP_Gender="1",
        GP_GpCode="Y123452",
        GP_Title="Mr",
        GP_Forenames="Paul Philip",
        GP_Surname="Davies",
        GP_AddressLine1="1 Trevelyan Square",
        GP_AddressLine2="",
        GP_AddressLine3="",
        GP_AddressLine4="Leeds",
        GP_AddressLine5="West Yorkshire",
        GP_PostCode="LS1 6UP",
        IsComparisonCompleted=False,
        GP_HaCipher="TEST",
        GP_TransactionDate="2021-01-01",
        GP_TransactionTime="01:00:00",
        GP_TransactionId="1235",
        GP_PreviousSurname="",
        GP_DrugsDispensedMarker=False,
    )

    response = lambda_handler.pds_hydrate("50", record)
    expected_response = "Retrieved PDS data for JobId: 50, PatientId: 51, NhsNumber: 8000000008"

    assert response["message"] == expected_response

    actual = Demographics.get("51", "50").attribute_values

    expected = {
        "Id": "51",
        "JobId": "50",
        "NhsNumber": "8000000008",
        "GP_DateOfBirth": "20091022",
        "GP_Gender": "1",
        "GP_GpCode": "Y123452",
        "GP_Title": "Mr",
        "GP_Forenames": "Paul Philip",
        "GP_Surname": "Davies",
        "GP_AddressLine1": "1 Trevelyan Square",
        "GP_AddressLine2": "",
        "GP_AddressLine3": "",
        "GP_AddressLine4": "Leeds",
        "GP_AddressLine5": "West Yorkshire",
        "GP_PostCode": "LS1 6UP",
        "IsComparisonCompleted": False,
        "GP_HaCipher": "TEST",
        "GP_TransactionDate": "2021-01-01",
        "GP_TransactionTime": "01:00:00",
        "GP_TransactionId": "1235",
        "GP_PreviousSurname": "",
        "GP_DrugsDispensedMarker": False,
        "PDS_GpCode": "Y123451",
        "PDS_GpRegisteredDate": "2012-05-22",
        "PDS_Surname": "Davies",
        "PDS_Forenames": ["Paul", "Philip"],
        "PDS_Titles": ["Mr"],
        "PDS_Gender": "male",
        "PDS_DateOfBirth": "2009-10-22",
        "PDS_Sensitive": "R",
        "PDS_Address": [
            "1 Trevelyan Square",
            "Leeds",
            "West Yorkshire",
        ],
        "PDS_PostCode": "LS1 6UP",
        "GP_RegistrationStatus": "Partnership Mismatch",
        "PDS_Version": "2",
    }

    assert actual == expected


def test_gp_registration_Deducted_Patient_Match_in_demographics_table(
    upload_pds_mock_data_to_s3,
    create_dynamodb_tables,
    create_LR08_demographic_comparison_lambda,
    lambda_handler,
):

    record = Demographics(
        Id="52",
        JobId="50",
        NhsNumber="7000000007",
        GP_DateOfBirth="19231121",
        GP_Gender="1",
        GP_GpCode="Y123452",
        GP_Title="Miss",
        GP_Forenames="Nikki-Stevens",
        GP_Surname="Pavey",
        GP_AddressLine1="19 Main Street",
        GP_AddressLine2="",
        GP_AddressLine3="Logan",
        GP_AddressLine4="Durham",
        GP_AddressLine5="London",
        GP_PostCode="ZE3 9JY",
        IsComparisonCompleted=False,
        GP_HaCipher="TEST",
        GP_TransactionDate="2021-01-01",
        GP_TransactionTime="01:00:00",
        GP_TransactionId="1236",
        GP_PreviousSurname="",
        GP_DrugsDispensedMarker=False,
    )

    response = lambda_handler.pds_hydrate("50", record)
    expected_response = "Retrieved PDS data for JobId: 50, PatientId: 52, NhsNumber: 7000000007"

    assert response["message"] == expected_response

    actual = Demographics.get("52", "50").attribute_values

    expected = {
        "Id": "52",
        "JobId": "50",
        "NhsNumber": "7000000007",
        "GP_DateOfBirth": "19231121",
        "GP_Gender": "1",
        "GP_GpCode": "Y123452",
        "GP_Title": "Miss",
        "GP_Forenames": "Nikki-Stevens",
        "GP_Surname": "Pavey",
        "GP_AddressLine1": "19 Main Street",
        "GP_AddressLine2": "",
        "GP_AddressLine3": "Logan",
        "GP_AddressLine4": "Durham",
        "GP_AddressLine5": "London",
        "GP_PostCode": "ZE3 9JY",
        "IsComparisonCompleted": False,
        "GP_HaCipher": "TEST",
        "GP_TransactionDate": "2021-01-01",
        "GP_TransactionTime": "01:00:00",
        "GP_TransactionId": "1236",
        "GP_PreviousSurname": "",
        "GP_DrugsDispensedMarker": False,
        "PDS_GpRegisteredDate": "2012-05-22",
        "PDS_Surname": "Pavey",
        "PDS_Forenames": ["Nikki-Stevens"],
        "PDS_Titles": ["Miss"],
        "PDS_Gender": "female",
        "PDS_DateOfBirth": "1923-11-21",
        "PDS_Sensitive": "REDACTED",
        "PDS_Address": [
            "19 Main Street",
            "Logan",
            "Durham",
            "London",
        ],
        "PDS_PostCode": "ZE3 9JY",
        "GP_RegistrationStatus": "Deducted Patient Match",
        "PDS_Version": "6",
    }

    assert actual == expected


def test_gp_registration_Unmatched_in_demographics_table(
    upload_pds_mock_data_to_s3,
    create_dynamodb_tables,
    create_LR08_demographic_comparison_lambda,
    lambda_handler,
):

    record = Demographics(
        Id="53",
        JobId="50",
        NhsNumber="6000000006",
        GP_DateOfBirth="19231121",
        GP_Gender="1",
        GP_GpCode="Y123452",
        GP_Title="Miss",
        GP_Forenames="Janet",
        GP_Surname="Wardle",
        GP_AddressLine1="18 Main Street",
        GP_AddressLine2="",
        GP_AddressLine3="Logan",
        GP_AddressLine4="Durham",
        GP_AddressLine5="London",
        GP_PostCode="ZE3 9JY",
        IsComparisonCompleted=False,
        GP_HaCipher="TEST",
        GP_TransactionDate="2021-01-01",
        GP_TransactionTime="01:00:00",
        GP_TransactionId="1236",
        GP_PreviousSurname="",
        GP_DrugsDispensedMarker=False,
    )

    response = lambda_handler.pds_hydrate("50", record)
    expected_response = "PDS data not found for JobId: 50, PatientId: 53, NhsNumber: 6000000006"

    assert response["message"] == expected_response

    actual = Demographics.get("53", "50").attribute_values
    expected = {
        "Id": "53",
        "JobId": "50",
        "NhsNumber": "6000000006",
        "GP_DateOfBirth": "19231121",
        "GP_Gender": "1",
        "GP_GpCode": "Y123452",
        "GP_Title": "Miss",
        "GP_Forenames": "Janet",
        "GP_Surname": "Wardle",
        "GP_AddressLine1": "18 Main Street",
        "GP_AddressLine2": "",
        "GP_AddressLine3": "Logan",
        "GP_AddressLine4": "Durham",
        "GP_AddressLine5": "London",
        "GP_PostCode": "ZE3 9JY",
        "IsComparisonCompleted": True,
        "GP_HaCipher": "TEST",
        "GP_TransactionDate": "2021-01-01",
        "GP_TransactionTime": "01:00:00",
        "GP_TransactionId": "1236",
        "GP_PreviousSurname": "",
        "GP_DrugsDispensedMarker": False,
        "GP_RegistrationStatus": "Unmatched",
    }

    assert actual == expected
