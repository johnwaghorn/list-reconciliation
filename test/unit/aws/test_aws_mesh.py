import os

import boto3
import pytest
from mesh import AWSMESHMailbox, InvalidFilename
from moto import mock_s3

AWS_REGION = os.getenv("AWS_REGION")
MESH_BUCKET = os.getenv("MESH_BUCKET")


class LoggerStub:
    def write_log(
        self,
        log_reference="UTI9999",
        error_list=None,
        log_row_dict=None,
        severity_threshold_override=None,
        process_name=None,
    ):
        print(log_reference, error_list, log_row_dict, severity_threshold_override, process_name)


@pytest.fixture
def s3():
    with mock_s3():
        client = boto3.client("s3", region_name=AWS_REGION)
        client.create_bucket(
            Bucket=MESH_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )
        yield


def test_AWSMESHMailbox_send_message(s3):
    mesh = AWSMESHMailbox("X26OT188", LoggerStub())
    s3_client = boto3.client("s3")

    # Overwrite ignores existing file
    s3_client.put_object(Bucket=MESH_BUCKET, Key="outbound_X26OT188_to_ABC123/test.txt", Body="")

    mesh.send_message("ABC123", "test.txt", "content", overwrite=True)

    file = (
        s3_client.get_object(Bucket=MESH_BUCKET, Key="outbound_X26OT188_to_ABC123/test.txt")["Body"]
        .read()
        .decode("utf-8")
    )

    assert file == "content"


def test_AWSMESHMailbox_send_message_existing_raises_IOError(s3):
    mesh = AWSMESHMailbox("X26OT188", LoggerStub())

    mesh.send_message("ABC123", "test.txt", "content", overwrite=False)

    with pytest.raises(IOError):
        mesh.send_message("ABC123", "test.txt", "content", overwrite=False)


def test_AWSMESHMailbox_send_message_bad_name_raises_InvalidFilename(s3):
    mesh = AWSMESHMailbox("X26OT188", LoggerStub())

    with pytest.raises(InvalidFilename):
        mesh.send_message("ABC123", "not_allowed_this_slash/test.txt", "content")


def test_AWSMESHMailbox_send_messages(s3):
    mesh = AWSMESHMailbox("X26OT188", LoggerStub())
    mesh.send_messages(
        "ABC123", (("test.txt", "content"), ("test2.txt", "content2")), overwrite=True
    )

    s3_client = boto3.client("s3")
    file1 = (
        s3_client.get_object(Bucket=MESH_BUCKET, Key="outbound_X26OT188_to_ABC123/test.txt")["Body"]
        .read()
        .decode("utf-8")
    )

    file2 = (
        s3_client.get_object(Bucket=MESH_BUCKET, Key="outbound_X26OT188_to_ABC123/test2.txt")[
            "Body"
        ]
        .read()
        .decode("utf-8")
    )

    assert file1 == "content"
    assert file2 == "content2"
    assert mesh.get_pending_messages("ABC123") == ["test.txt", "test2.txt"]


def test_AWSMESHMailbox_inbox(s3):
    mesh = AWSMESHMailbox("X26OT188", LoggerStub())

    assert mesh.inbox == "inbound_X26OT188"


def test_AWSMESHMailbox_outbox(s3):
    mesh = AWSMESHMailbox("X26OT188", LoggerStub())

    assert mesh.outbox("ABC123") == "outbound_X26OT188_to_ABC123"


def test_AWSMESHMailbox_bucket(s3):
    mesh = AWSMESHMailbox("X26OT188", LoggerStub())

    assert mesh.bucket == MESH_BUCKET


def test_AWSMESHMailbox_list_messages(s3):
    mesh = AWSMESHMailbox("X26OT188", LoggerStub())
    s3_client = boto3.client("s3")
    s3_client.put_object(Bucket=MESH_BUCKET, Key="inbound_X26OT188/inbound_message.txt", Body="")
    s3_client.put_object(Bucket=MESH_BUCKET, Key="inbound_X26OT188/another_message.txt", Body="")

    assert sorted(mesh.list_messages()) == sorted(["another_message.txt", "inbound_message.txt"])
