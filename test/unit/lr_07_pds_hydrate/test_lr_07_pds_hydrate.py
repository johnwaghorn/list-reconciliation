import os

import pytest
from database.models import Demographics

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "..", "_data", "unit")

REGION_NAME = "eu-west-2"
JOB_ID = "50"


def test_write_into_table(
    upload_pds_mock_data_to_s3,
    create_LR08_demographic_comparison_lambda,
    create_dynamodb_tables,
    lambda_context,
    lambda_handler,
    mock_response,
):
    lambda_handler.job_id = JOB_ID

    record = Demographics(
        "50",
        "50",
        NhsNumber="9000000009",
        GP_DateOfBirth="20101025",
        GP_Gender="2",
        GP_GpPracticeCode="Y123452",
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

    response = lambda_handler.pds_hydrate(record)

    assert response["message"] == "LR07 Lambda application stopped"
    assert response["job_id"] == JOB_ID

    actual = Demographics.get("50", "50").attribute_values

    expected = {
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
            "Leeds",
            "City Centre",
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
    mock_response,
):
    lambda_handler.job_id = JOB_ID

    record = Demographics(
        Id="51",
        JobId="50",
        NhsNumber="8000000008",
        GP_DateOfBirth="20091022",
        GP_Gender="1",
        GP_GpPracticeCode="Y123452",
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

    response = lambda_handler.pds_hydrate(record)

    assert response["message"] == "LR07 Lambda application stopped"
    assert response["job_id"] == JOB_ID

    actual = Demographics.get("51", "50").attribute_values

    expected = {
        "Id": "51",
        "JobId": JOB_ID,
        "NhsNumber": "8000000008",
        "GP_DateOfBirth": "20091022",
        "GP_Gender": "1",
        "GP_GpPracticeCode": "Y123452",
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
        "PDS_GpPracticeCode": "Y123451",
        "PDS_GpRegisteredDate": "2012-05-22",
        "PDS_Surname": "Davies",
        "PDS_Forenames": ["Paul", "Philip"],
        "PDS_Titles": ["Mr"],
        "PDS_Gender": "male",
        "PDS_DateOfBirth": "2009-10-22",
        "PDS_Sensitive": "U",
        "PDS_Address": [
            "1 Trevelyan Square",
            "",
            "",
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
    mock_response,
):
    lambda_handler.job_id = JOB_ID

    record = Demographics(
        Id="52",
        JobId="50",
        NhsNumber="9449306060",
        GP_DateOfBirth="19231121",
        GP_Gender="1",
        GP_GpPracticeCode="Y123452",
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

    response = lambda_handler.pds_hydrate(record)

    assert response["message"] == "LR07 Lambda application stopped"
    assert response["job_id"] == JOB_ID

    actual = Demographics.get("52", "50").attribute_values

    expected = {
        "IsComparisonCompleted": False,
        "GP_AddressLine1": "19 Main Street",
        "GP_AddressLine2": "",
        "GP_AddressLine3": "Logan",
        "GP_AddressLine4": "Durham",
        "GP_AddressLine5": "London",
        "GP_DateOfBirth": "19231121",
        "GP_DrugsDispensedMarker": False,
        "GP_Forenames": "Nikki-Stevens",
        "GP_Gender": "1",
        "GP_GpPracticeCode": "Y123452",
        "GP_HaCipher": "TEST",
        "GP_PostCode": "ZE3 9JY",
        "GP_PreviousSurname": "",
        "GP_RegistrationStatus": "Deducted Patient Match",
        "GP_Surname": "Pavey",
        "GP_Title": "Miss",
        "GP_TransactionDate": "2021-01-01",
        "GP_TransactionId": "1236",
        "GP_TransactionTime": "01:00:00",
        "Id": "52",
        "JobId": "50",
        "NhsNumber": "9449306060",
        "PDS_Address": [],
        "PDS_DateOfBirth": "",
        "PDS_Forenames": [],
        "PDS_Gender": "",
        "PDS_GpPracticeCode": "",
        "PDS_GpRegisteredDate": "",
        "PDS_PostCode": "",
        "PDS_Sensitive": "REDACTED",
        "PDS_Surname": "",
        "PDS_Titles": [],
        "PDS_Version": "",
    }
    assert actual == expected


def test_gp_registration_Unmatched_in_demographics_table(
    upload_pds_mock_data_to_s3,
    create_dynamodb_tables,
    create_LR08_demographic_comparison_lambda,
    lambda_handler,
    mock_jwt_encode,
    mock_auth_post,
    mock_response,
):
    lambda_handler.job_id = JOB_ID

    record = Demographics(
        Id="53",
        JobId="50",
        NhsNumber="6000000006",
        GP_DateOfBirth="19231121",
        GP_Gender="1",
        GP_GpPracticeCode="Y123452",
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

    response = lambda_handler.pds_hydrate(record)

    assert response["message"] == "LR07 Lambda application stopped"
    assert response["job_id"] == JOB_ID

    actual = Demographics.get("53", "50").attribute_values
    expected = {
        "Id": "53",
        "JobId": JOB_ID,
        "NhsNumber": "6000000006",
        "GP_DateOfBirth": "19231121",
        "GP_Gender": "1",
        "GP_GpPracticeCode": "Y123452",
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


@pytest.mark.parametrize(
    "test_id,nhs_number,Id,job_id,expected_demographics",
    [
        (
            "REDACTED",
            "9449306060",
            "54",
            "50",
            {
                "IsComparisonCompleted": False,
                "GP_AddressLine1": "1 Trevelyan Square",
                "GP_AddressLine2": "Boar's Head Lane",
                "GP_AddressLine3": "City Centre",
                "GP_AddressLine4": "Leeds",
                "GP_AddressLine5": "West Yorkshire",
                "GP_DateOfBirth": "20101025",
                "GP_DrugsDispensedMarker": False,
                "GP_Forenames": "Jane",
                "GP_Gender": "2",
                "GP_GpPracticeCode": "Y123452",
                "GP_HaCipher": "TEST",
                "GP_PostCode": "LS1 6AE",
                "GP_PreviousSurname": "TEST",
                "GP_RegistrationStatus": "Deducted Patient Match",
                "GP_Surname": "Smith",
                "GP_Title": "Mrs",
                "GP_TransactionDate": "2021-01-01",
                "GP_TransactionId": "1234",
                "GP_TransactionTime": "01:00:00",
                "Id": "54",
                "JobId": "50",
                "NhsNumber": "9449306060",
                "PDS_Sensitive": "REDACTED",
                "PDS_Address": [],
                "PDS_DateOfBirth": "",
                "PDS_Forenames": [],
                "PDS_Gender": "",
                "PDS_GpPracticeCode": "",
                "PDS_GpRegisteredDate": "",
                "PDS_PostCode": "",
                "PDS_Surname": "",
                "PDS_Titles": [],
                "PDS_Version": "",
            },
        ),
        (
            "restricted",
            "9449310378",
            "55",
            "50",
            {
                "IsComparisonCompleted": False,
                "GP_AddressLine1": "1 Trevelyan Square",
                "GP_AddressLine2": "Boar's Head Lane",
                "GP_AddressLine3": "City Centre",
                "GP_AddressLine4": "Leeds",
                "GP_AddressLine5": "West Yorkshire",
                "GP_DateOfBirth": "20101025",
                "GP_DrugsDispensedMarker": False,
                "GP_Forenames": "Jane",
                "GP_Gender": "2",
                "GP_GpPracticeCode": "Y123452",
                "GP_HaCipher": "TEST",
                "GP_PostCode": "LS1 6AE",
                "GP_PreviousSurname": "TEST",
                "GP_RegistrationStatus": "Deducted Patient Match",
                "GP_Surname": "Smith",
                "GP_Title": "Mrs",
                "GP_TransactionDate": "2021-01-01",
                "GP_TransactionId": "1234",
                "GP_TransactionTime": "01:00:00",
                "Id": "55",
                "JobId": "50",
                "NhsNumber": "9449310378",
                "PDS_Address": [],
                "PDS_DateOfBirth": "1982-05-25",
                "PDS_Forenames": ["MALEAH"],
                "PDS_Gender": "Male",
                "PDS_GpPracticeCode": "",
                "PDS_GpRegisteredDate": "",
                "PDS_PostCode": "",
                "PDS_Sensitive": "R",
                "PDS_Surname": "GEELAN",
                "PDS_Titles": ["MS"],
                "PDS_Version": "2",
            },
        ),
    ],
)
def test_sensitive_patients(
    lambda_handler,
    create_LR08_demographic_comparison_lambda,
    create_dynamodb_tables,
    nhs_number,
    test_id,
    job_id,
    Id,
    mock_response,
    expected_demographics,
):
    lambda_handler.job_id = JOB_ID

    record = Demographics(
        Id=Id,
        JobId=job_id,
        NhsNumber=nhs_number,
        GP_DateOfBirth="20101025",
        GP_Gender="2",
        GP_GpPracticeCode="Y123452",
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

    response = lambda_handler.pds_hydrate(record)

    assert response["status"] == "success"
    assert response["message"] == "LR07 Lambda application stopped"
    assert response["job_id"] == JOB_ID
