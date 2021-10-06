import json
import uuid
from datetime import datetime

import boto3
from botocore.exceptions import ClientError


def upload_to_s3(email: str, filename: str, bucket) -> bool:

    s3 = boto3.client("s3")
    try:
        s3.put_object(Body=email, Bucket=bucket, Key=filename)
        return True
    except ClientError as e:
        raise e


def to_json(service_index: str, to: list, subject: str, body) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return json.dumps(
        {
            "service_index": service_index.upper(),
            "timestamp": timestamp,
            "to": to,
            "subject": subject,
            "body": body,
        }
    )


def generate_filename() -> str:
    guid = str(uuid.uuid4())
    return f"{guid}.json"
