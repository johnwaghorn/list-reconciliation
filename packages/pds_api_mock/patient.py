import traceback
from typing import Union

from fastapi import FastAPI, Response, status
from mangum import Mangum
from pds_api_mock.errors import error_response_404, error_response_500
from pds_api_mock.model import ErrorResponse, MockFHIRResponse
from pds_api_mock.pds_data import (
    filter_redacted_patients,
    filter_restricted_patients,
    filter_unrestricted_patients,
    filter_very_restricted_patients,
    get_mock_data,
)
from pydantic import BaseModel

sensitive_marker_filter_funcs = {
    "R": filter_restricted_patients,
    "V": filter_very_restricted_patients,
    "REDACTED": filter_redacted_patients,
    "U": filter_unrestricted_patients,
}

app = FastAPI(title="PDS API Mock", root_path="/")
handler = Mangum(app)


@app.get(
    "/patient/{nhs_number}",
    response_model=Union[MockFHIRResponse, ErrorResponse],
    response_model_exclude_none=True,
)
def get_pds_patient_record(nhs_number: str, response: Response):
    try:
        patient_record = _get_patient(nhs_number)
        if patient_record:
            resp, response.status_code = _filter_patient(patient_record)
            return resp
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return error_response_404()
    except Exception:
        resp, response.status_code = error_response_500(traceback.format_exc())
        return resp


# TODO this needs to be rewritten: store and retrieve from Dynamo? S3 Select? Some sort of local lookup?
def _get_patient(nhs_number):
    try:
        for row in get_mock_data():
            if row["NHS_NUMBER"] == nhs_number:
                return row
    except Exception:
        raise ValueError("PDS data unavailable")


def _filter_patient(patient_record) -> tuple[BaseModel, int]:
    patient_sensitive_marker = patient_record["SENSITIVE_FLAG"]

    filter_func = sensitive_marker_filter_funcs.get(patient_sensitive_marker, None)
    if filter_func:
        return filter_func(patient_record)

    return error_response_500("Patient Sensitive Status unknown")
