import os
import json

import boto3
from botocore.exceptions import ClientError
from retrying import retry


def ssm_client(region):
    return boto3.client("ssm", region_name=region)


def ssm_retry_exception(exception):
    if isinstance(exception, (ClientError)):
        if "ThrottlingException" in str(exception) or "ConnectionClosedError" in str(exception):
            return True


@retry(
    wait_exponential_multiplier=100,
    wait_exponential_max=2000,
    retry_on_exception=ssm_retry_exception,
    stop_max_attempt_number=10,
)
def get_ssm_params(ssm_path, region):
    ssm = ssm_client(region)

    params_result = ssm.get_parameters_by_path(
        Path=ssm_path,
        Recursive=False,
        WithDecryption=True,
    )
    params_dict = params_result.get("Parameters", {})
    ssm_params_dict = {}
    for entry in params_dict:
        name = entry.get("Name", None)
        if name:
            var_name = os.path.basename(name)
            ssm_params_dict[var_name] = entry.get("Value", None)
    return ssm_params_dict


@retry(
    wait_exponential_multiplier=100,
    wait_exponential_max=2000,
    retry_on_exception=ssm_retry_exception,
    stop_max_attempt_number=10,
)
def put_ssm_params(ssm_path, data_string, region, string_type="SecureString"):
    try:
        ssm = ssm_client(region)
        ssm.put_parameter(
            Name=ssm_path, Value=json.dumps(data_string), Type=string_type, Overwrite=True
        )
        return True
    except ClientError as err:
        # ignore TooManyUpdates Exceptions as other lambda have already updated the token
        # there is no way to catch TooManyUpdates exception in botocore exceptions  hence clientError as
        # suggested by AWS
        if "TooManyUpdates" in str(err):
            pass
