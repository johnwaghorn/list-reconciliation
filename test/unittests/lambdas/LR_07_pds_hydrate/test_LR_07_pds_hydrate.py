import os

import pytest

from lambdas.LR_07_pds_hydrate.pds_hydrate import pds_hydrate
from utils.models import Demographics
from utils.logger import success

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")

REGION_NAME = "eu-west-2"


PDS_COLUMNS = (
    "PDS_GpCode",
    "PDS_GpRegisteredDate",
    "PDS_Surname",
    "PDS_Forenames",
    "PDS_Titles",
    "PDS_Gender",
    "PDS_DateOfBirth",
    "PDS_IsSensitive",
    "PDS_Address",
    "PDS_PostCode",
    "GP_RegistrationStatus",
)


def test_write_into_table(
    upload_pds_mock_data_to_s3, demographics_records, create_LR08_demographic_comparison_lambda
):

    response = pds_hydrate("9000000009", "50", "50")
    expected_response = success(
        "Retrieved PDS data for NhsNumber: 9000000009, JobId: 50, PatientId: 50"
    )

    assert response == expected_response

    record = Demographics.get("50", "50").attribute_values

    actual = {k: v for k, v in record.items() if k in PDS_COLUMNS}

    expected = {
        "PDS_GpCode": "Y123452",
        "PDS_GpRegisteredDate": "2012-05-22",
        "PDS_Surname": "Smith",
        "PDS_Forenames": ["Jane"],
        "PDS_Titles": ["Mrs"],
        "PDS_Gender": "female",
        "PDS_DateOfBirth": "2010-10-22",
        "PDS_IsSensitive": False,
        "PDS_Address": [
            "1 Trevelyan Square",
            "Boar Lane",
            "City Centre",
            "Leeds",
            "West Yorkshire",
        ],
        "PDS_PostCode": "LS1 6AE",
        "GP_RegistrationStatus": "Matched",
    }

    assert actual == expected


def test_record_doesnt_exist_raises_DemographicsDoesNotExist(
    upload_pds_mock_data_to_s3, demographics_records, create_LR08_demographic_comparison_lambda
):
    with pytest.raises(Demographics.DoesNotExist):
        pds_hydrate("9000000009", "500", "500")


def test_gp_registration_Partnership_Mismatch_in_demographics_table(
    upload_pds_mock_data_to_s3, demographics_records, create_LR08_demographic_comparison_lambda
):

    response = pds_hydrate("8000000008", "50", "51")
    expected_response = success(
        "Retrieved PDS data for NhsNumber: 8000000008, JobId: 50, PatientId: 51"
    )

    assert response == expected_response

    record = Demographics.get("51", "50").attribute_values

    actual = {k: v for k, v in record.items() if k in PDS_COLUMNS}

    expected = {
        "PDS_GpCode": "Y123451",
        "PDS_GpRegisteredDate": "2012-05-22",
        "PDS_Surname": "Davies",
        "PDS_Forenames": ["Paul", "Philip"],
        "PDS_Titles": ["Mr"],
        "PDS_Gender": "male",
        "PDS_DateOfBirth": "2009-10-22",
        "PDS_IsSensitive": True,
        "PDS_Address": [
            "1 Trevelyan Square",
            "Leeds",
            "West Yorkshire",
        ],
        "PDS_PostCode": "LS1 6UP",
        "GP_RegistrationStatus": "Partnership Mismatch",
    }

    assert actual == expected


def test_gp_registration_Deducted_Patient_Match_in_demographics_table(
    upload_pds_mock_data_to_s3, demographics_records, create_LR08_demographic_comparison_lambda
):

    response = pds_hydrate("7000000007", "50", "52")
    expected_response = success(
        "Retrieved PDS data for NhsNumber: 7000000007, JobId: 50, PatientId: 52"
    )

    assert response == expected_response

    record = Demographics.get("52", "50").attribute_values

    actual = {k: v for k, v in record.items() if k in PDS_COLUMNS}

    expected = {
        "PDS_GpRegisteredDate": "2012-05-22",
        "PDS_Surname": "Pavey",
        "PDS_Forenames": ["Nikki-Stevens"],
        "PDS_Titles": ["Miss"],
        "PDS_Gender": "female",
        "PDS_DateOfBirth": "1923-11-21",
        "PDS_IsSensitive": True,
        "PDS_Address": [
            "19 Main Street",
            "Logan",
            "Durham",
            "London",
        ],
        "PDS_PostCode": "ZE3 9JY",
        "GP_RegistrationStatus": "Deducted Patient Match",
    }

    assert actual == expected


def test_gp_registration_Unmatched_in_demographics_table(
    upload_pds_mock_data_to_s3, demographics_records, create_LR08_demographic_comparison_lambda
):

    response = pds_hydrate("6000000006", "50", "53")
    expected_response = success(
        "PDS data not found for NhsNumber: 6000000006, JobId: 50, PatientId: 53"
    )

    assert response == expected_response

    record = Demographics.get("53", "50").attribute_values
    actual = record["GP_RegistrationStatus"]
    expected = "Unmatched"

    assert actual == expected
