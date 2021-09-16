import csv
import os
from typing import Union

import boto3
import botocore.exceptions
from fastapi import status
from pds_api_mock.errors import error_response_404, error_response_500
from pds_api_mock.model import (
    GP,
    Address,
    Enum,
    ErrorResponse,
    Identifier,
    Meta,
    MetaSecurity,
    MockFHIRResponse,
    Name,
    Period,
)


class SensitiveMarkers(Enum):
    R = "restricted"
    U = "unrestricted"
    V = "very restricted"
    SENSITIVE = "R"
    VERY_SENSITIVE = "V"
    REDACTED = "REDACTED"
    UNRESTRICTED = "U"


PDS_DATA_BUCKET = os.getenv("PDS_BUCKET")
PDS_DATA_FILE = os.getenv("PDS_DATA_FILE")

s3_client = boto3.resource("s3")

# TODO remove this when _get_patient is rewritten
def get_mock_data():
    try:
        bucket = s3_client.Bucket(PDS_DATA_BUCKET)
        obj = bucket.Object(key=PDS_DATA_FILE)

        pds_api_data = obj.get()["Body"].read().decode("utf-8-sig").splitlines()
        reader = csv.DictReader(pds_api_data, delimiter=",")
        return reader

    except (
        botocore.exceptions.ClientError,
        botocore.exceptions.ParamValidationError,
    ) as exc:
        raise exc


def filter_redacted_patients(record):
    resp = error_response_404(record)
    return resp, status.HTTP_404_NOT_FOUND


def filter_restricted_patients(
    record,
) -> Union[tuple[MockFHIRResponse, int], tuple[ErrorResponse, int]]:
    try:
        return (
            MockFHIRResponse(
                id=record["NHS_NUMBER"],
                identifier=[Identifier(value=record["NHS_NUMBER"])],
                meta=Meta(
                    security=[
                        MetaSecurity(
                            code=record["SENSITIVE_FLAG"],
                            display=SensitiveMarkers[record["SENSITIVE_FLAG"]].value,
                        )
                    ]
                ),
                gender=record["GENDER"],
                name=[
                    Name(
                        id="124",
                        use="usual",
                        given=[record["GIVEN_NAME"]],
                        family=record["FAMILY_NAME"],
                        prefix=[record["TITLE"]],
                    )
                ],
                birthDate=record["DATE_OF_BIRTH"],
                deceasedDateTime=record["DATE_OF_DEATH"],
            ),
            status.HTTP_200_OK,
        )
    except Exception as e:
        return error_response_500(str(e))


def filter_very_restricted_patients(record):
    try:
        return (
            MockFHIRResponse(
                id=record["NHS_NUMBER"],
                identifier=[Identifier(value=record["NHS_NUMBER"])],
                meta=Meta(
                    security=[
                        MetaSecurity(
                            code=record["SENSITIVE_FLAG"],
                            display=SensitiveMarkers[record["SENSITIVE_FLAG"]].value,
                        )
                    ]
                ),
                gender="unknown",
            ),
            status.HTTP_200_OK,
        )
    except Exception as e:
        return error_response_500(str(e))


def filter_unrestricted_patients(record):
    try:
        return (
            MockFHIRResponse(
                id=record["NHS_NUMBER"],
                identifier=[Identifier(value=record["NHS_NUMBER"])],
                meta=Meta(
                    security=[
                        MetaSecurity(
                            code=record["SENSITIVE_FLAG"],
                            display=SensitiveMarkers[record["SENSITIVE_FLAG"]].value,
                        )
                    ]
                ),
                gender=record["GENDER"],
                name=[
                    Name(
                        id="124",
                        use="usual",
                        given=[record["GIVEN_NAME"]],
                        family=record["FAMILY_NAME"],
                        prefix=[record["TITLE"]],
                    )
                ],
                birthDate=record["DATE_OF_BIRTH"],
                deceasedDateTime=record["DATE_OF_DEATH"],
                generalPractitioner=[
                    GP(
                        identifier=Identifier(
                            system="https://fhir.nhs.uk/Id/ods-organization-code",
                            value=record["PRIMARY_CARE_CODE"],
                            period=Period(),
                        )
                    )
                ],
                address=[
                    Address(
                        id="456",
                        line=[
                            record["ADDRESS_LINE_1"],
                            record["ADDRESS_LINE_2"],
                            record["ADDRESS_LINE_3"],
                            record["ADDRESS_LINE_4"],
                            record["ADDRESS_LINE_5"],
                        ],
                        postalCode=record["POST_CODE"],
                    )
                ],
            ),
            status.HTTP_200_OK,
        )
    except Exception as e:
        return error_response_500(str(e))
