import json
import os

import boto3
from getgauge.python import Messages, step

from utils import InputFolderType
from .lr_02_lambda_val_parse import create_gp_file
from .tf_aws_resources import get_terraform_output

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")

LR_01_BUCKET = get_terraform_output("lr_01_bucket")
LR_01_BUCKET_INBOUND = get_terraform_output("lr_01_bucket_inbound")
LR_25_LAMBDA_ARN = get_terraform_output("LR_25_lambda_arn")
MESH_BUCKET = "list-rec-preprod-mesh"
MESH_INBOUND = get_terraform_output("mesh_inbound")


s3 = boto3.client("s3")
lambda_ = boto3.client("lambda")


@step("send <filename> to mesh inbound folder")
def send_file_to_mesh_outbound_folder(filename):
    temp_destdir = os.path.join(DATA, filename)
    row = "DOW~1"
    temp_destdir = create_gp_file(filename, row)
    global destination_filename
    destination_filename = os.path.basename(temp_destdir)

    try:
        s3.upload_file(
            Filename=temp_destdir,
            Bucket=MESH_BUCKET,
            Key=os.path.join(MESH_INBOUND, destination_filename),
        )
        Messages.write_message("Upload Successful")

    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step("invoke lambda LR-25")
def invoke_lambda_lr_25():
    response = lambda_.invoke(FunctionName=LR_25_LAMBDA_ARN, LogType="Tail", Payload=json.dumps({}))
    for key, value in response.items():
        if key == "ResponseMetadata":
            assert int(value["HTTPStatusCode"]) == int(200)


@step("connect to pass folder and check the destination file has loaded")
def connect_to_pass_folder_and_check_for_destination_folder():
    try:
        waiter = s3.get_waiter("object_exists")
        waiter.wait(
            Bucket=LR_01_BUCKET,
            Key=os.path.join(InputFolderType.PASS.value, destination_filename),
        )
        Messages.write_message(
            f"Object exists: s3://{os.path.join(LR_01_BUCKET, InputFolderType.PASS.value, destination_filename)}"
        )
    except FileNotFoundError as e:
        Messages.write_message(
            f"Object not found: s3://{os.path.join(LR_01_BUCKET, InputFolderType.PASS.value, destination_filename)}"
        )
        raise e
