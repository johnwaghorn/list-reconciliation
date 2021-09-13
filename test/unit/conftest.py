import datetime
import json
import os

import boto3
import jwt
import pytest
import requests
from moto import mock_ssm
from spine_aws_common import LambdaApplication

from pds_api.pds_api import PDSAPI, PDSParamStore
from unit.mock_responses import MockPostRepsone, MockResponse

SSM_PARAM_PREFIX = os.getenv("SSM_STORE_PREFIX")
REGION_NAME = os.environ.get("AWS_REGION")


@pytest.fixture(scope="function")
def ssm():
    with mock_ssm():
        yield boto3.client("ssm", region_name=REGION_NAME)


@pytest.fixture(scope="function")
def mock_pds_private_key(ssm):
    ssm.put_parameter(
        Name=f"{SSM_PARAM_PREFIX}{PDSParamStore.PDS_PRIVATE_KEY.value}",
        Value="'-----BEGIN PUBLIC KEY-----\n test\n-----END PUBLIC KEY-----'",
        Type="SecureString",
        Overwrite=True,
    )
    yield


@pytest.fixture(scope="function")
def mock_jwt_encode(monkeypatch):
    def mock_return(*args, **kwargs):
        return "mock_response"

    monkeypatch.setattr(jwt, "encode", mock_return)


@pytest.fixture
def mock_pds_app_key(ssm):
    ssm.put_parameter(
        Name=f"{SSM_PARAM_PREFIX}{PDSParamStore.PDS_APP_KEY.value}",
        Value="test",
        Type="SecureString",
        Overwrite=True,
    )
    yield


@pytest.fixture
def mock_pds_access_token(ssm):
    ssm.put_parameter(
        Name=f"{SSM_PARAM_PREFIX}{PDSParamStore.PDS_ACCESS_TOKEN.value}",
        Value=json.dumps(
            {
                "access_token": "this_is_a_test_token",
                "expires_in": "599",
                "token_type": "Bearer",
                "issued_at": "1627882540",
            }
        ),
        Type="SecureString",
        Overwrite=True,
    )
    yield


@pytest.fixture()
def create_mock_ssm_valid_access_token(ssm):
    now = datetime.datetime.now()
    in_future = now + datetime.timedelta(0, 599)
    future_timestamp = str(in_future.timestamp())[:10]
    token = json.dumps(
        {
            "access_token": "this_is_a_test_token",
            "expires_in": "599",
            "token_type": "Bearer",
            "issued_at": future_timestamp,
        }
    )
    ssm.put_parameter(
        Name=f"{SSM_PARAM_PREFIX}{PDSParamStore.PDS_ACCESS_TOKEN.value}",
        Value=token,
        Type="SecureString",
        Overwrite=True,
    )


@pytest.fixture()
def create_mock_ssm_expired_access_token(ssm):
    now = datetime.datetime.now()
    in_past = now - datetime.timedelta(0, 599)
    past_timestamp = str(in_past.timestamp())[:10]
    token = json.dumps(
        {
            "access_token": "this_is_a_test_token",
            "expires_in": "599",
            "token_type": "Bearer",
            "issued_at": past_timestamp,
        }
    )
    ssm.put_parameter(
        Name=f"{SSM_PARAM_PREFIX}{PDSParamStore.PDS_ACCESS_TOKEN.value}",
        Value=token,
        Type="SecureString",
        Overwrite=True,
    )


@pytest.fixture
def mock_response(monkeypatch):
    """Requests.get() mocked to return {"mock_key":"mock_response"}."""

    def mock_get(*args, **kwargs):
        return MockResponse(args)

    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture
def mock_auth_post(monkeypatch):
    """Requests.post() mocked to return {"mock_key":"mock_response"}."""

    def mock_post(*args, **kwargs):
        return MockPostRepsone(args)

    monkeypatch.setattr(requests, "post", mock_post)


@pytest.fixture(scope="function")
def pds_api():
    lambda_app = LambdaApplication()
    api = PDSAPI(lambda_app.system_config)
    api.auth_required = False
    return api


@pytest.fixture
def pds_url():
    return "https://sandbox.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient"


@pytest.fixture(scope="session")
def lambda_context():
    return {"aws_request_id": "TEST"}


@pytest.fixture
def mock_email(monkeypatch):
    monkeypatch.setattr("nhs_mail_relay.send_email", lambda w, x, y, z: None)
