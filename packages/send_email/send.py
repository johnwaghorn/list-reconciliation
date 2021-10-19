import os

from exchangelib import DELEGATE, Account, Configuration, Credentials, Mailbox, Message
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
            "email_addresses": ["example@nhs.com", "example2@nhs.com"],
            "subject": subject,
            "message": body,
            }
    Returns: None

    """
    credentials = Credentials(username, password)
    try:
        config = _get_config(credentials)
        account = _get_account(username, config)

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


def _get_config(credentials: Credentials):
    config = Configuration(server="outlook.office365.com", credentials=credentials)
    return config


def _get_account(username, configuration: Configuration):
    account = Account(
        primary_smtp_address=username,
        config=configuration,
        autodiscover=False,
        access_type=DELEGATE,
    )
    return account
