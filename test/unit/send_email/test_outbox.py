import pytest
from freezegun import freeze_time
from send_email import outbox


@freeze_time("2021-09-27 11:20:24")
@pytest.mark.parametrize(
    "service, to, subject, body,expected",
    (
        (
            "LR-07",
            [
                "example_email@nhs.net",
                "example_email2@nhs.net",
                "example_email3@nhs.net",
            ],
            "Very important email",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            '{"service": "LR-07", "timestamp": "20210927112024", "to": ["example_email@nhs.net", '
            '"example_email2@nhs.net", '
            '"example_email3@nhs.net"], "subject": "Very important email", "body": "Lorem ipsum dolor sit amet, '
            'consectetur adipiscing elit."}',
        ),
        (
            "LR-14",
            ["example_email@nhs.net"],
            "Very important email",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            '{"service": "LR-14", "timestamp": "20210927112024", "to": ["example_email@nhs.net"], '
            '"subject": "Very important email", "body": "Lorem ipsum dolor sit amet, '
            'consectetur adipiscing elit."}',
        ),
    ),
)
def test_format(service, to, subject, body, expected):
    actual = outbox.to_json(service, to, subject, body)
    assert actual == expected
