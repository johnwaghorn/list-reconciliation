import logging
import sys

from exchangelib import Account, Credentials, FaultTolerance, Mailbox, Message
from exchangelib.autodiscover import Autodiscovery
from spine_aws_common.logger import Logger

log = logging.getLogger("ExchangeEmailLogger")


def send_email(username: str, password: str, event: dict, log_object: Logger):
    log_object.write_log(
        "UTI9995",
        None,
        {
            "logger": "ExchangeEmail",
            "level": "INFO",
            "message": f"Retrieved NHSMail credentials from AWS Secrets Manager for {username}",
        },
    )
    Autodiscovery.INITIAL_RETRY_POLICY = FaultTolerance(max_wait=10)
    credentials = Credentials(username, password)
    try:
        account = _get_account(credentials, log_object)
        log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "ExchangeEmail",
                "level": "INFO",
                "message": "Connected to Exchange account and cached configuration",
            },
        )
    except Exception:
        log_object.write_log(
            "UTI9995",
            sys.exc_info(),
            {
                "logger": "ExchangeEmail",
                "level": "ERROR",
                "message": "Could not connect to Exchange account",
            },
        )
        raise

    try:
        recipients = [Mailbox(email_address=x) for x in event["email_addresses"]]
        message = Message(
            account=account,
            subject=event["subject"],
            body=f"{event['message']}",
            to_recipients=recipients,
        )

        message.send()
    except Exception:
        log_object.write_log(
            "UTI9995",
            sys.exc_info(),
            {
                "logger": "ExchangeEmail",
                "level": "ERROR",
                "message": "Could not send email",
            },
        )
        raise
    else:
        log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "ExchangeEmail",
                "level": "INFO",
                "message": "Successfully sent email",
            },
        )


def _get_account(credentials: Credentials, log_object: Logger):
    log_object.write_log(
        "UTI9995",
        None,
        {
            "logger": "ExchangeEmail",
            "level": "INFO",
            "message": "Autodiscovering account data",
        },
    )
    account = Account(
        primary_smtp_address=credentials.username, credentials=credentials, autodiscover=True
    )
    return account
