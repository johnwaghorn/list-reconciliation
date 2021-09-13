import os

import pytest

PDS_API_URL = os.getenv("PDS_API_URL")
AWS_REGION = os.getenv("AWS_REGION")

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "..", "lambdas", "data")


def test_expired_token(create_mock_ssm_valid_access_token, pds_api):
    response = pds_api._is_token_invalid()
    assert not response


def test_valid_token(create_mock_ssm_expired_access_token, pds_api):
    response = pds_api._is_token_invalid()
    assert response


def test_get_access_token(
    mock_pds_app_key,
    mock_pds_private_key,
    mock_pds_access_token,
    mock_jwt_encode,
    mock_auth_post,
    pds_api,
    create_mock_ssm_valid_access_token,
):
    response = pds_api.get_access_token()
    expected_keys = ["access_token", "expires_in", "token_type", "issued_at"]
    assert all(keys in expected_keys for keys in response.keys())


def test_get_new_access_token(
    mock_pds_app_key,
    mock_pds_private_key,
    mock_pds_access_token,
    create_mock_ssm_expired_access_token,
    mock_jwt_encode,
    mock_auth_post,
    pds_api,
):
    response = pds_api.get_access_token()
    expected_keys = ["access_token", "expires_in", "token_type", "issued_at"]
    assert all(keys in expected_keys for keys in response.keys())


def test_pds_record(
    mock_pds_app_key,
    mock_pds_private_key,
    mock_pds_access_token,
    mock_jwt_encode,
    mock_auth_post,
    pds_api,
    mock_response,
):
    response = pds_api.get_pds_record("9000000009", "test-job-id")
    expected_response = {
        "surname": "Smith",
        "forenames": ["Jane"],
        "title": ["Mrs"],
        "date_of_birth": "2010-10-22",
        "gender": "female",
        "address": ["1 Trevelyan Square", "Boar Lane", "Leeds", "City Centre", "West Yorkshire"],
        "postcode": "LS1 6AE",
        "gp_practicecode": "Y123452",
        "gp_registered_date": "2012-05-22",
        "sensitive": "U",
        "version": "1",
    }
    assert response == expected_response


@pytest.mark.parametrize(
    "id,url,expected",
    [
        ("prod", "https://api.service.nhs.uk/personal-demographics/FHIR/R4/", "prod-1"),
        ("ref", "https://ref.api.service.nhs.uk/personal-demographics/FHIR/R4/", "ref-1"),
        ("int", "https://int.api.service.nhs.uk/personal-demographics/FHIR/R4/", "int-1"),
        ("sandbox", "https://sandbox.api.service.nhs.uk/personal-demographics/FHIR/R4/", None),
    ],
)
def test_key_identifier(
    id, url, expected, mock_pds_app_key, mock_pds_private_key, mock_pds_access_token, pds_api
):
    pds_api.pds_url = url
    kid = pds_api.get_key_identifier()

    assert kid == expected
