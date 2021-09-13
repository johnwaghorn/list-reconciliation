import os
from typing import IO, Generator

import boto3
import botocore
from spine_aws_common.logger import Logger

MESH_BUCKET = os.environ["MESH_BUCKET"]


class InvalidFilename(Exception):
    pass


class AWSMESHMailbox:
    def __init__(self, mailbox_id: str, spine_lambda_application_logger: Logger):
        self.mailbox_id = mailbox_id
        self.s3 = boto3.client("s3")
        self.log_object = spine_lambda_application_logger

    @property
    def bucket(self) -> str:
        return MESH_BUCKET

    def send_message(self, destination_id: str, filename: str, file: IO, overwrite=False):
        if "/" in filename:
            raise InvalidFilename("Filename cannot contain '/'")

        outbox = self.outbox(destination_id)
        key = f"{outbox}/{filename}"

        if not overwrite:
            if filename in self.get_pending_messages(destination_id):
                raise OSError(f"File {key} already exists, message not sent")

        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "AWSMESHMailbox",
                "level": "INFO",
                "message": f"Sending message {filename} to {outbox}",
            },
        )
        self.s3.put_object(Bucket=MESH_BUCKET, Key=key, Body=file)
        return f"s3://{MESH_BUCKET}/{key}"

    def send_messages(self, destination_id: str, files: list[tuple[str, IO]], overwrite=False):
        for filename, file in files:
            self.send_message(destination_id, filename, file, overwrite=overwrite)

    def outbox(self, destination_id: str) -> str:
        return f"outbound_{self.mailbox_id}_to_{destination_id}"

    @property
    def inbox(self) -> str:
        return f"inbound_{self.mailbox_id}"

    def list_messages(self, prefix=None) -> list[str]:
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "AWSMESHMailbox",
                "level": "INFO",
                "message": f"Fetching message keys from {self.inbox}",
            },
        )
        return [
            os.path.basename(obj["Key"])
            for obj in self.s3.list_objects_v2(Bucket=MESH_BUCKET, Prefix=prefix or self.inbox).get(
                "Contents", []
            )
        ]

    def get_messages(self) -> Generator[botocore.response.StreamingBody, None, None]:
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "AWSMESHMailbox",
                "level": "INFO",
                "message": f"Fetching messages from {self.inbox}",
            },
        )
        for file in self.list_messages():
            yield self.get_message(file)

    def get_message(self, filename: str) -> botocore.response.StreamingBody:
        key = f"{self.inbox}/{filename}"
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "AWSMESHMailbox",
                "level": "INFO",
                "message": f"Fetching message from {key}",
            },
        )

        return self.s3.get_object(Bucket=MESH_BUCKET, Key=key)["Body"]

    def get_pending_messages(self, destination_id):
        return self.list_messages(prefix=self.outbox(destination_id))


def get_mesh_mailboxes(mesh_mapping, workflow_id):
    for obj in mesh_mapping:
        for outbound_mapping in obj["outbound_mappings"]:
            if workflow_id == outbound_mapping["workflow_id"]:
                return obj["id"], outbound_mapping["dest_mailbox"]
