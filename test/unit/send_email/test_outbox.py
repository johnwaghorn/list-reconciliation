import pytest
from freezegun import freeze_time
from send_email import outbox


@freeze_time("2021-09-27 11:20:24")
@pytest.mark.parametrize(
    "service_index, to, subject, body,expected",
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
            '{"service_index": "LR-07", "timestamp": "20210927112024", "to": ["example_email@nhs.net", '
            '"example_email2@nhs.net", '
            '"example_email3@nhs.net"], "subject": "Very important email", "body": "Lorem ipsum dolor sit amet, '
            'consectetur adipiscing elit."}',
        ),
        (
            "LR-14",
            ["example_email@nhs.net"],
            "Very important email",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            '{"service_index": "LR-14", "timestamp": "20210927112024", "to": ["example_email@nhs.net"], '
            '"subject": "Very important email", "body": "Lorem ipsum dolor sit amet, '
            'consectetur adipiscing elit."}',
        ),
    ),
)
def test_format(service_index, to, subject, body, expected):
    actual = outbox.to_json(service_index, to, subject, body)
    assert actual == expected


def test_filename():
    expected = 41
    actual = len(outbox.generate_filename())
    assert actual == expected
