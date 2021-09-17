from typing import Union

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


def filter_redacted_patients(record):
    resp = error_response_404(record)
    return resp, status.HTTP_404_NOT_FOUND


def filter_restricted_patients(
    record,
) -> Union[tuple[MockFHIRResponse, int], tuple[ErrorResponse, int]]:
    try:
        return (
            MockFHIRResponse(
                id=record["nhs_number"],
                identifier=[Identifier(value=record["nhs_number"])],
                meta=Meta(
                    security=[
                        MetaSecurity(
                            code=record["sensitive_flag"],
                            display=SensitiveMarkers[record["sensitive_flag"]].value,
                        )
                    ]
                ),
                gender=record["gender"],
                name=[
                    Name(
                        id="124",
                        use="usual",
                        given=[record["given_name"]],
                        family=record["family_name"],
                        prefix=[record["title"]],
                    )
                ],
                birthDate=record["date_of_birth"],
                deceasedDateTime=record["date_of_death"],
            ),
            status.HTTP_200_OK,
        )
    except Exception as e:
        return error_response_500(str(e))


def filter_very_restricted_patients(record):
    try:
        return (
            MockFHIRResponse(
                id=record["nhs_number"],
                identifier=[Identifier(value=record["nhs_number"])],
                meta=Meta(
                    security=[
                        MetaSecurity(
                            code=record["sensitive_flag"],
                            display=SensitiveMarkers[record["sensitive_flag"]].value,
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
                id=record["nhs_number"],
                identifier=[Identifier(value=record["nhs_number"])],
                meta=Meta(
                    security=[
                        MetaSecurity(
                            code=record["sensitive_flag"],
                            display=SensitiveMarkers[record["sensitive_flag"]].value,
                        )
                    ]
                ),
                gender=record["gender"],
                name=[
                    Name(
                        id="124",
                        use="usual",
                        given=[record["given_name"]],
                        family=record["family_name"],
                        prefix=[record["title"]],
                    )
                ],
                birthDate=record["date_of_birth"],
                deceasedDateTime=record["date_of_death"],
                generalPractitioner=[
                    GP(
                        identifier=Identifier(
                            system="https://fhir.nhs.uk/Id/ods-organization-code",
                            value=record["primary_care_code"],
                            period=Period(),
                        )
                    )
                ],
                address=[
                    Address(
                        id="456",
                        line=[
                            record["address_line_1"],
                            record["address_line_2"],
                            record["address_line_3"],
                            record["address_line_4"],
                            record["address_line_5"],
                        ],
                        postalCode=record["post_code"],
                    )
                ],
            ),
            status.HTTP_200_OK,
        )
    except Exception as e:
        return error_response_500(str(e))
