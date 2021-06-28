import pytest


@pytest.fixture
def pds_url():
    return "https://sandbox.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient"
