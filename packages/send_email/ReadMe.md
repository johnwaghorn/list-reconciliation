# send_email

send_email is a Python package for generating and sending an email.

With given arguments, 'to_outbox' will create a json file and upload it to an S3 bucket,
used as an outbox, with the aim that the email be sent from the outbox later.

Using the 'send' function, an email can be sent to desired recipients, via an Exchange server user account.
## Requirements

Use a package manager e.g. [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install boto3, botocore, exchangelib
```

## Usage

```python
from send_email.send import to_outbox

service = "spine service"
to = ["example_email@nhs.net"]
subject = "a very important email"
body = "a long body"

to_outbox(service, to, subject, body)
# returns 'boolean'
```

```python
from send_email.send import send

username = "example_username"
password = "example_password"
event = {
    "email_addresses": ["example_email@nhs.net"],
    "subject": "a very important email",
    "message": "pls read my email",
}

send(username, password, event)
```
