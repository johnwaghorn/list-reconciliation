import pytest


@pytest.fixture
def pds_url():
    return "https://sandbox.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient"


@pytest.fixture(scope="session")
def lambda_context():
    return {"aws_request_id": "TEST"}


@pytest.fixture
def mock_email(monkeypatch):
    monkeypatch.setattr(
        "services.send_email_exchangelib.send_exchange_email", lambda w, x, y, z: None
    )
