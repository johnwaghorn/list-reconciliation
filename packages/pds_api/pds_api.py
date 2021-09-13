import datetime
import json
import uuid
from enum import Enum
from json import JSONDecodeError
from time import time
from typing import Optional, Union

import jwt
import requests
from aws.ssm import get_ssm_params, put_ssm_params
from jsonpath_ng import parse
from retrying import retry

SIGNING_ALG = "RS512"
PDS_URL_PATH = "personal-demographics/FHIR/R4"
PDS_TOKEN_URL_PATH = "oauth2/token"


class PDSAPIError(Exception):
    pass


class ExpiredTokenError(Exception):
    pass


class TooManyRequests(Exception):
    pass


class UnknownError(Exception):
    pass


class PDSParamStore(Enum):
    PDS_APP_KEY = "pds_api_app_key"
    PDS_PRIVATE_KEY = "pds_api_private_key"
    PDS_ACCESS_TOKEN = "pds_api_access_token"


class SensitiveMarkers(Enum):
    REDACTED = "REDACTED"
    RESTRICTED = "R"
    VERY_RESTRICTED = "V"


PDS_ERROR_RESPONSE_MAPPING = {
    "400": {
        "INVALID_RESOURCE_ID": "issue.[*].details.coding.[*].display",
        "UNSUPPORTED_SERVICE": "issue.[*].details.coding.[*].display",
        "MISSING_VALUE": "issue.[*].diagnostics",
        "INVALID_VALUE": "issue.[*].diagnostics",
    },
    "401": {"ACCESS_DENIED": "issue.[*].details.coding.[*].display"},
    "403": {"INVALID_VALUE": "issue.[*].details.coding.[*].display"},
    "404": {
        "RESOURCE_NOT_FOUND": "issue.[*].details.coding.[*].display",
        "INVALIDATED_RESOURCE": "issue.[*].details.coding.[*].display",
    },
    "408": {"UNABLE_TO_CALL_SERVICE": "issue.[*].details.coding.[*].display"},
    "429": {"TOO_MANY_REQUESTS": "issue.[*].details.coding.[*].display"},
}

PDS_DATA_MAPPING_CONFIG = {
    "fields": [
        {"name": "surname", "value": "name.[*].family", "default": ""},
        {"name": "forenames", "value": "name.[*].given", "default": []},
        {"name": "title", "value": "name.[*].prefix", "default": []},
        {"name": "date_of_birth", "value": "birthDate", "default": ""},
        {"name": "gender", "value": "gender", "default": ""},
        {"name": "address", "value": "address.[*].line", "default": []},
        {"name": "postcode", "value": "address.[*].postalCode", "default": ""},
        {
            "name": "gp_practicecode",
            "value": "generalPractitioner.[*].identifier.value",
            "default": "",
        },
        {
            "name": "gp_registered_date",
            "value": "generalPractitioner.[*].identifier.period.start",
            "default": "",
        },
        {"name": "sensitive", "value": "meta.security.[*].code", "default": ""},
        {"name": "version", "value": "meta.versionId", "default": ""},
    ]
}


class PDSAPI:
    def __init__(self, system_config: dict):
        self.pds_data = {}
        if not isinstance(system_config, dict):
            raise PDSAPIError("System config not available, exiting")
        self.ssm_store_path = system_config["SSM_STORE_PREFIX"]
        self.region = system_config["AWS_REGION"]
        self.pds_base_url = system_config["PDS_BASE_URL"]
        self.pds_url = f"{self.pds_base_url}/{PDS_URL_PATH}/Patient"
        self.pds_token_url = f"{self.pds_base_url}/{PDS_TOKEN_URL_PATH}"
        self.auth_required = "sandbox" not in self.pds_url
        self.ssm_params = get_ssm_params(self.ssm_store_path, self.region)

    def get_access_token(self):
        """
        Gets access token from the Auth URL

        Return: Bearer Token
        """

        try:
            if self._is_token_invalid():
                claims = {
                    "sub": self.ssm_params[PDSParamStore.PDS_APP_KEY.value],
                    "iss": self.ssm_params[PDSParamStore.PDS_APP_KEY.value],
                    "jti": str(uuid.uuid4()),
                    "aud": self.pds_token_url,
                    "exp": int(time()) + 300,
                }
                additional_headers = {"kid": self.get_key_identifier()}
                j = jwt.encode(
                    claims,
                    self.ssm_params[PDSParamStore.PDS_PRIVATE_KEY.value],
                    algorithm=SIGNING_ALG,
                    headers=additional_headers,
                )
                form_data = {
                    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                    "client_assertion": j,
                    "grant_type": "client_credentials",
                }

                # TODO ensure this response is not an error
                # {"error": "invalid_request", "error_description": "Invalid iss/sub claims in JWT", "message_id": "rrt-6068836616924912677-c-geu2-30273-4334972-1"}
                response = requests.post(self.pds_token_url, data=form_data)
                token = response.json()
                put_ssm_params(
                    f"{self.ssm_store_path}{PDSParamStore.PDS_ACCESS_TOKEN.value}",
                    region="eu-west-2",
                    data_string=token,
                )
            else:
                # token is either expired or not set
                token = json.loads(self.ssm_params["pds_api_access_token"])

            return token

        except Exception as e:
            raise PDSAPIError(e) from e

    @retry(
        wait_exponential_multiplier=100,
        wait_exponential_max=2000,
        retry_on_exception=lambda x: isinstance(
            x, (ExpiredTokenError, TooManyRequests, UnknownError)
        ),
        stop_max_attempt_number=20,
    )
    def get_pds_record(self, nhs_number: str, job_id: uuid) -> Optional[dict[str, str]]:
        """
        Calls FHIR/PDS API URL using patient's NHS NUMBER and returns the JSON including
        patients patients

        For PDS data with Security code value 'R' and 'V' , treat as patients patient
        FOR REDACTED patient , API sends 404 with code as INVALIDATED_RESOURCE

         Args:
            nhs_number: 10-digit NHS number of the record to retrieve.
            job_id: Job id

        Returns:
                only 'patients' marker for patients patients and other fields as None
               for 'unrestricted' record , all details are send
               for non existent patient , return empty dictionary

        """

        try:
            headers = {"X-Request-ID": str(uuid.uuid4()), "X-Correlation-ID": job_id}

            if self.auth_required:
                token = self.get_access_token()
                auth_header = {"Authorization": f"Bearer {token['access_token']}"}
                headers.update(auth_header)

            response = requests.get(f"{self.pds_url}/{nhs_number}", headers=headers)
        except requests.exceptions.ConnectionError:
            raise PDSAPIError(f"Connection error: {self.pds_url}")

        status = response.status_code

        if response.ok:
            self.pds_data = response.json()
            return self.convert_pds_to_list_rec_data()
        elif not str(status).startswith("2"):
            return self.process_non_2xx_responses(response, status, nhs_number, job_id)
        else:
            raise PDSAPIError(
                f"Patient {nhs_number} error_code: {status}, error_details:{response.text}"
            )

    def get_key_identifier(self):
        """
        creates Key identifier for JWT token

        Returns:
             key identifier string
        """
        kid = {
            "ref.api.service.nhs.uk": "ref-1",
            "int.api.service.nhs.uk": "int-1",
            "api.service.nhs.uk": "prod-1",
        }
        if self.pds_url:
            base_url = self.pds_url.split("/")[2]
            return kid.get(base_url)

    def convert_pds_to_list_rec_data(self) -> dict[str, str]:
        """
        creates the pds json data from PDS API data
        It sets value to empty string '' for fields
        not send by PDS API and empty list [] for
        address,title and forenames

        Returns:
            dict pds data
        """
        formatted_pds_data: dict = {}
        field = PDS_DATA_MAPPING_CONFIG["fields"]
        for item in field:
            pds_data_value = self.parse_json_data(item["value"])
            formatted_pds_data.update(
                {item["name"]: pds_data_value if pds_data_value else item["default"]}
            )
        return formatted_pds_data

    def parse_json_data(self, field: str) -> Optional[str]:
        """
        Find the value of the field passed on

        Args:
            field is a jsonpath field
            e.g.  test= { 'x':10, y:[ {'z':7, 'T':99}] }
            to filter 99
            expression would be
           'y.[*].T' or 'y.[0].T'

        Returns:
             Value of a nested json/dict as per the JSON Path
             if no match is found, it returns default value set to '' (empty string)

        """
        json_expr = parse(field)
        for item in json_expr.find(self.pds_data):
            return item.value

    def process_non_2xx_responses(
        self, response: requests, status_code: int, nhs_number: str, job_id: uuid
    ) -> Union[dict[str, str], None]:
        """
        Process all http status codes with non-2xx responses
        if status code is not 2xx and there is JSONDecodeError
        the implication is that API hasn't returned any json (data).
        in that case just return None to Lambda

            Args:
                response: Response object from PDS API
                status_code: int , HTTP status codes
                nhs_number: str, Patients NHS number
                job_id:uuid, job id

            Returns:
                list rec pds data for REDACTED Patients
                or  Raises TooManyParameters or TokenError or PDSAPIError or JSONDecodeError
                or None for patient not found
        """
        try:
            self.pds_data = response.json()
            error_code = self.parse_json_data("issue.[*].details.coding.[*].code")
            json_path = PDS_ERROR_RESPONSE_MAPPING[str(status_code)][error_code]
            error_details = self.parse_json_data(json_path)

            if status_code == 404 and error_code == "INVALIDATED_RESOURCE":
                # Patient Record is REDACTED
                redacted_patient_data = self.convert_pds_to_list_rec_data()
                redacted_patient_data.update(
                    {"sensitive": SensitiveMarkers.REDACTED.value}
                )  # update dict with REDACTED
                return redacted_patient_data

            elif status_code == 404 and error_code == "RESOURCE_NOT_FOUND":
                # PDS data not found for the patient
                return

            elif status_code == 401 and error_details == "Access Token expired":
                raise ExpiredTokenError("Expired token, fetch again")

            elif status_code == 429:
                raise TooManyRequests("Too many requests")

            elif error_code == "UNKNOWN_ERROR":
                message = f"API response for patient {nhs_number}: http_status_code: {status_code}, error_code: {error_code}, error_details:{error_details}"
                raise UnknownError(message)

            else:
                message = f"API response for patient {nhs_number}: http_status_code: {status_code}, error_code: {error_code}, error_details:{error_details}"
                raise PDSAPIError(message)

        except JSONDecodeError:
            return

    def _is_token_invalid(self) -> bool:
        """
        Checks if stored token has not expired
        on first run , there is no token set ,
        Fetch again if the token doesn't have required fields
        e.g issued_at or expires_in
        return True to fetch a new one

        Return:
            bool
        """
        try:
            token = json.loads(self.ssm_params[PDSParamStore.PDS_ACCESS_TOKEN.value])
            return self.is_token_expired(token)

        except JSONDecodeError:
            # First run, token is not set
            return True

    @staticmethod
    def is_token_expired(token):
        """
        Checks if token is still valid,
        Token is valid for 10 minutes
        duration is mentioned in expires_in field

        Args:
            token: dict
            return bool
            if expired return True else False
        """
        time_now = datetime.datetime.now()
        try:
            token_issue_time = str(token["issued_at"])[:10]
            token_expire_in_seconds = int(token["expires_in"])
        except KeyError:
            # Token issued doesn't have required field
            return True
        issue_datetime = datetime.datetime.fromtimestamp(int(token_issue_time))
        token_expiry_time = issue_datetime + datetime.timedelta(0, token_expire_in_seconds)
        return time_now > token_expiry_time
