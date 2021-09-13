import json

import boto3

from aws.ssm import get_ssm_params, put_ssm_params
from unit.conftest import SSM_PARAM_PREFIX, REGION_NAME


def test_get_ssm(mock_pds_private_key, mock_pds_app_key, mock_pds_access_token):
    param = get_ssm_params(SSM_PARAM_PREFIX, REGION_NAME)
    expected = {
        "pds_api_app_key": "test",
        "pds_api_private_key": "'-----BEGIN PUBLIC KEY-----\n test\n-----END PUBLIC KEY-----'",
        "pds_api_access_token": '{"access_token": "this_is_a_test_token", "expires_in": "599", "token_type": "Bearer", "issued_at": "1627882540"}',
    }
    assert param == expected


def test_put_param(mock_pds_access_token):
    param_name = f"{SSM_PARAM_PREFIX}pds_api_access_token"
    data_string = {"test": "token"}
    put_ssm_params(param_name, data_string, string_type="SecureString", region=REGION_NAME)

    client = boto3.client("ssm")
    data = client.get_parameter(Name=param_name, WithDecryption=True)

    assert data_string == json.loads(data["Parameter"]["Value"])
