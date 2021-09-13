from datetime import datetime, timedelta

LAST_RESET = datetime.now()
RESPONSES = 0
MAX_RESPONSES_PER_SECOND = 15


def respond():
    global LAST_RESET
    global RESPONSES

    if datetime.now() - LAST_RESET >= timedelta(seconds=1):
        RESPONSES = 0
        LAST_RESET = datetime.now()

    RESPONSES += 1

    if RESPONSES > MAX_RESPONSES_PER_SECOND:
        return 429, False
    else:
        return 200, True


class MockResponse:
    def __init__(self, mock_url):

        self.patient_id = mock_url[0].split("/")[7]
        self.patients = {
            "9449306060": ("REDACTED", "REDACTED"),
            "9449310610": ("V", "very restricted"),
            "9449310378": ("R", "restricted"),
            "9000000009": ("U", "unrestricted"),
            "8000000008": ("U", "unrestricted"),
            "7000000007": ("U", "unrestricted"),
            "6000000006": ("U", "RESOURCE_NOT_FOUND"),
            "1000000100": ("TOO_MANY_REQUESTS", "TOO_MANY_REQUESTS"),
        }
        if (
            self.patients[self.patient_id][0] == "REDACTED"
            or self.patients[self.patient_id][1] == "RESOURCE_NOT_FOUND"
        ):
            self.status_code = 404
            self.ok = False
        elif self.patients[self.patient_id][1] == "TOO_MANY_REQUESTS":
            self.status_code, self.ok = respond()
        else:
            self.status_code = 200
            self.ok = True

    def restricted(self):

        data = {
            "resourceType": "Patient",
            "id": self.patient_id,
            "identifier": [
                {"value": self.patient_id, "system": "https://fhir.nhs.uk/Id/nhs-number"}
            ],
            "meta": {
                "versionId": "2",
                "security": [
                    {
                        "system": "https://www.hl7.org/fhir/valueset-security-labels.html",
                        "code": self.patients[self.patient_id][0],
                        "display": self.patients[self.patient_id][0],
                    }
                ],
            },
            "gender": "unknown" if self.patients[self.patient_id][0] == "V" else "Male",
        }
        if self.patients[self.patient_id][0] == "R":
            restricted = {
                "name": [
                    {
                        "id": "124",
                        "use": "usual",
                        "given": ["MALEAH"],
                        "family": "GEELAN",
                        "prefix": ["MS"],
                    }
                ],
                "birthDate": "1982-05-25",
                "deceasedDateTime": "",
            }
            return data | restricted
        else:
            return data

    @staticmethod
    def redacted():
        return {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "details": {
                        "coding": [
                            {
                                "version": "1",
                                "code": "INVALIDATED_RESOURCE",
                                "display": "Resource Id is invalid",
                                "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                            }
                        ]
                    },
                    "severity": "error",
                    "code": "value",
                }
            ],
        }

    @staticmethod
    def too_many_requests():
        return {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "details": {
                        "coding": [
                            {
                                "version": "1",
                                "code": "TOO_MANY_REQUESTS",
                                "display": "TOO_MANY_REQUESTS",
                                "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                            }
                        ]
                    },
                    "severity": "error",
                    "code": "value",
                }
            ],
        }

    def unrestricted_90000000009(self):
        return {
            "resourceType": "Patient",
            "id": self.patient_id,
            "identifier": [
                {"value": self.patient_id, "system": "https://fhir.nhs.uk/Id/nhs-number"}
            ],
            "meta": {
                "versionId": "1",
                "security": [
                    {
                        "system": "https://www.hl7.org/fhir/valueset-security-labels.html",
                        "code": "U",
                        "display": "unrestricted",
                    }
                ],
            },
            "name": [
                {
                    "id": "124",
                    "use": "usual",
                    "given": ["Jane"],
                    "family": "Smith",
                    "prefix": ["Mrs"],
                }
            ],
            "gender": "female",
            "birthDate": "2010-10-22",
            "deceasedDateTime": "",
            "generalPractitioner": [
                {
                    "id": "254406A3",
                    "type": "Organization",
                    "identifier": {
                        "value": "Y123452",
                        "period": {"start": "2012-05-22", "end": "2021-12-31"},
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    },
                }
            ],
            "address": [
                {
                    "id": "456",
                    "use": "home",
                    "line": [
                        "1 Trevelyan Square",
                        "Boar Lane",
                        "Leeds",
                        "City Centre",
                        "West Yorkshire",
                    ],
                    "postalCode": "LS1 6AE",
                    "extension": [],
                }
            ],
        }

    def unrestricted_70000000007(self):
        return {
            "resourceType": "Patient",
            "id": self.patient_id,
            "identifier": [
                {"value": self.patient_id, "system": "https://fhir.nhs.uk/Id/nhs-number"}
            ],
            "meta": {
                "versionId": "6",
                "security": [
                    {
                        "system": "https://www.hl7.org/fhir/valueset-security-labels.html",
                        "code": "U",
                        "display": "unrestricted",
                    }
                ],
            },
            "name": [
                {
                    "id": "124",
                    "use": "usual",
                    "given": ["Nikki-Stevens"],
                    "family": "Pavey",
                    "prefix": ["Miss"],
                }
            ],
            "gender": "Female",
            "birthDate": "1923-11-21",
            "deceasedDateTime": "",
            "generalPractitioner": [
                {
                    "id": "254406A3",
                    "type": "Organization",
                    "identifier": {
                        "period": {"start": "2012-05-22", "end": "2021-12-31"},
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    },
                }
            ],
            "address": [
                {
                    "id": "456",
                    "use": "home",
                    "line": [
                        "19 Main Street",
                        "Logan",
                        "Durham",
                        "London",
                    ],
                    "postalCode": "ZE3 9JY",
                    "extension": [],
                }
            ],
        }

    def unrestricted_60000000006(self):
        return {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "details": {
                        "coding": [
                            {
                                "version": "1",
                                "code": "RESOURCE_NOT_FOUND",
                                "display": "Resource Id is invalid",
                                "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                            }
                        ]
                    },
                    "severity": "error",
                    "code": "value",
                }
            ],
        }

    def unrestricted_80000000008(self):
        return {
            "resourceType": "Patient",
            "id": self.patient_id,
            "identifier": [
                {"value": self.patient_id, "system": "https://fhir.nhs.uk/Id/nhs-number"}
            ],
            "meta": {
                "versionId": "2",
                "security": [
                    {
                        "system": "https://www.hl7.org/fhir/valueset-security-labels.html",
                        "code": "U",
                        "display": "unrestricted",
                    }
                ],
            },
            "name": [
                {
                    "id": "124",
                    "use": "usual",
                    "given": ["Paul", "Philip"],
                    "family": "Davies",
                    "prefix": ["Mr"],
                }
            ],
            "gender": "male",
            "birthDate": "2009-10-22",
            "deceasedDateTime": "",
            "generalPractitioner": [
                {
                    "id": "254406A3",
                    "type": "Organization",
                    "identifier": {
                        "value": "Y123451",
                        "period": {"start": "2012-05-22", "end": "2021-12-31"},
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    },
                }
            ],
            "address": [
                {
                    "id": "456",
                    "use": "home",
                    "line": [
                        "1 Trevelyan Square",
                        "",
                        "",
                        "Leeds",
                        "West Yorkshire",
                    ],
                    "postalCode": "LS1 6UP",
                    "extension": [],
                }
            ],
        }

    def unrestricted_1000000100(self):
        return self.unrestricted_80000000008()

    def json(self):
        patient_status = self.patients[self.patient_id][0]
        if patient_status == "REDACTED":
            return self.redacted()
        elif patient_status == "U":
            func = {
                "9000000009": self.unrestricted_90000000009,
                "8000000008": self.unrestricted_80000000008,
                "7000000007": self.unrestricted_70000000007,
                "6000000006": self.unrestricted_60000000006,
            }
            return func[self.patient_id]()
        elif patient_status == "TOO_MANY_REQUESTS":
            if self.status_code == 429:
                return self.too_many_requests()
            else:
                return self.unrestricted_1000000100()
        else:
            return self.restricted()


class MockPostRepsone:
    def __init__(self, mock_url):
        pass

    def json(self):
        return {
            "access_token": "this_is_a_test_token",
            "expires_in": "599",
            "token_type": "Bearer",
            "issued_at": "1234567890",
        }
