import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl, validator


class Period(BaseModel):
    start = "2020-01-01"
    end = "2021-12-31"


class IdentifierExtensionCoding:
    system = "https://fhir.nhs.uk/R4/CodeSystem/UKCore-NHSNumberVerificationStatus"
    version = "1.0.0"
    code = "01"
    display = "Number present and verified"


class CodeConcept(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    coding: list[IdentifierExtensionCoding]


class IdentifierExtension(BaseModel):
    url: HttpUrl = HttpUrl(
        scheme="https",
        host="fhir.nhs.uk",
        url="/R4/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus",
    )
    valueCodeableConcept = CodeConcept


class Identifier(BaseModel):
    system = "https://fhir.nhs.uk/Id/nhs-number"
    value: Optional[str]
    period: Optional[Period]
    extension: Optional[list[IdentifierExtension]]


class ContactCoding:
    system: HttpUrl = HttpUrl(
        scheme="http",
        host="terminology.hl7.org",
        url="/CodeSystem/v2-0131",
    )
    code: str = "C"
    display: str = "Emergency Contact"


class Name(BaseModel):
    id: str
    use: str
    period: Optional[Period]
    given: list[str]
    family: str
    prefix: list[str]
    suffix: Optional[list[str]]


class MetaSecurity(BaseModel):
    system: HttpUrl = HttpUrl(
        scheme="https",
        host="www.hl7.org",
        url="/fhir/valueset-security-labels.html",
    )
    code: Optional[str]
    display: str


class Meta(BaseModel):
    versionId: str = "2"
    security: list[MetaSecurity]


class GP(BaseModel):
    id: str = "254406A3"
    type: str = "Organization"
    identifier: Identifier


class Telecom(BaseModel):
    id: str
    period: Period
    system: str = "phone"
    value: Optional[str] = ""
    use: str = "home"
    extension: Optional[list] = []


class ContactTelecom(BaseModel):
    system: str = "phone"
    value: Optional[str] = ""


class Contact(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    id: str
    period: Period
    relationship: list[ContactCoding]
    telecom: ContactTelecom


class Address(BaseModel):
    id: str
    period: Optional[Period]
    use: str = "home"
    line: list[str]
    postalCode: str
    extension: Optional[list] = []


class MockFHIRResponse(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    resourceType: str = "Patient"
    id: str
    identifier: list[Identifier]
    meta: Meta
    name: Optional[list[Name]] = None
    gender: str
    birthDate: Optional[str] = None
    multipleBirthInteger: Optional[int] = None
    deceasedDateTime: Optional[str] = None
    generalPractitioner: Optional[list[GP]] = None
    extension: Optional[list[Telecom]] = None
    telecom: Optional[list[str]] = None
    contact: Optional[list[str]] = None
    address: Optional[list[Address]] = None

    @validator("birthDate")
    def parse_birthdate(cls, value):
        try:
            datetime.datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            return datetime.datetime.strptime(value, "%Y%m%d").strftime("%Y-%m-%d")

    @validator("deceasedDateTime")
    def parse_deceased_date_time(cls, value):

        if not value:
            return value
        try:
            datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
            return value
        except ValueError:
            if len(value) <= 8:
                return datetime.datetime.strptime(value, "%Y%m%d").isoformat()
            else:
                return datetime.datetime.strptime(value, "%Y%m%d%H%M").isoformat()


class IssueDisplay(Enum):
    RESOURCE_NOT_FOUND = "Resource not found"
    INVALIDATED_RESOURCE = "Resource Id is invalid"
    SERVER_ERROR = "Server error"


class ErrorCoding(BaseModel):
    system = "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode"
    version: str = "1"
    code: str
    display: IssueDisplay


class Details(BaseModel):
    coding: list[ErrorCoding]


class Issue(BaseModel):
    severity = "error"
    code = "value"
    details: Details


class ErrorResponse(BaseModel):
    resourceType: str = "OperationOutcome"
    issue: list[Issue]
    diagnostics: Optional[str]
