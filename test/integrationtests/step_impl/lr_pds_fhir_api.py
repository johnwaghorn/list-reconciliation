import os
import requests
import json
from .test_helpers import PDS_API_ENV

from getgauge.python import step

URL = "https://sandbox.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient"
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", PDS_API_ENV)
PDSPATIENTFILE = "pds_api_response.json"


@step("trigger fhir r4 patient api for patient_id <patient_id> and assert response as expected")
def run_prd_fhir_get_patient_details_api(patient_id):
    url = URL + "/" + patient_id
    pds_url_headers = {
        "accept": "application/fhir+json",
        "NHSD-Session-URID": "555021935107",
        "X-Request-ID": "60E0B220-8136-4CA5-AE46-1D97EF59D068",
        "X-Correlation-ID": "11C46F5F-CDEF-4865-94B2-0EE0EDCC26DA",
    }

    response = requests.get(url, headers=pds_url_headers)

    response.raise_for_status()
    expected_response_file = os.path.join(DATA, PDSPATIENTFILE)

    with open(expected_response_file) as jsonfile:
        expected_response_body = json.load(jsonfile)
        actual_response_body = response.json()
        assert expected_response_body == actual_response_body, "Response payload doesnt match"


@step(
    "trigger fhir r4 patient api for patient_id <patient_id> and assert status code 412 for missing X-Request-ID"
)
def run_prd_fhir_get_patient_details_api(patient_id):
    url = URL + "/" + patient_id
    pds_url_headers = {
        "accept": "application/fhir+json",
        "NHSD-Session-URID": "555021935107",
        "X-Correlation-ID": "11C46F5F-CDEF-4865-94B2-0EE0EDCC26DA",
    }

    response = requests.get(url, headers=pds_url_headers)
    assert response.status_code == 412, f"Invalid code raised other than 412, instead raised {response.status_code}"
