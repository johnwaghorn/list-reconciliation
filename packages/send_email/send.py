import os

from exchangelib import Account, Credentials, FaultTolerance, Mailbox, Message
from exchangelib.autodiscover import Autodiscovery
from send_email.outbox import generate_filename, to_json, upload_to_s3


def to_outbox(service: str, to: list, subject: str, body, bucket=None) -> bool:
    """
    Send an email to an outbox, ready to be later relayed.
    Args:
        service (str): name of service that would like to send an email e.g. LR-07
        to (list) : recipients of the email
        subject (str): subject line of email
        body: body of email
        bucket: provide a s3 bucket to use an outbox or use a environment variable

    Returns:
        Bool
    """

    if bucket is None:
        bucket = os.environ["EMAIL_BUCKET"]

    email = to_json(service, to, subject, body)
    filename = generate_filename()
    return upload_to_s3(email, filename, bucket)


def send(username: str, password: str, event: dict):
    """
    Args:
        username: Usernames for authentication are of one of these forms:
            * PrimarySMTPAddress
            * WINDOMAIN\\username
            * User Principal Name (UPN)
        password: Clear-text password`
        event: {
            "email_addresses": ["rand@nhs.com", "rands@nhs.com"],
            "subject": subject,
            "message": body,
            }

    """
    Autodiscovery.INITIAL_RETRY_POLICY = FaultTolerance(max_wait=10)
    credentials = Credentials(username, password)
    try:
        account = _get_account(credentials)

    except Exception as e:
        raise e

    try:
        recipients = [Mailbox(email_address=x) for x in event["email_addresses"]]
        message = Message(
            account=account,
            subject=event["subject"],
            body=f"{event['message']}",
            to_recipients=recipients,
        )

        message.send()
    except Exception as e:
        raise e


def _get_account(credentials: Credentials):
    account = Account(
        primary_smtp_address=credentials.username,
        credentials=credentials,
        autodiscover=True,
    )
    return account
