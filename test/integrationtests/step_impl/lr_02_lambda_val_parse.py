from utils import InputFolderType
from getgauge.python import step
from getgauge.python import Messages
from utils.datetimezone import get_datetime_now
from .lr_beforehooks import use_waiters_check_object_exists

import boto3
import json
from tempfile import gettempdir
import os
from datetime import timedelta
from .tf_aws_resources import get_terraform_output

# On github
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)

REGION_NAME = "eu-west-2"
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
LR_01_BUCKET = get_terraform_output("lr_01_bucket")
LR_02_LAMBDA_ARN = get_terraform_output("lr_02_lambda_arn")

test_datetime = get_datetime_now()
temp_dir = gettempdir()
now = test_datetime - timedelta(hours=1)
day = "123456789ABCDEFGHIJKLMNOPQRSTUV"[now.day - 1]
month = "ABCDEFGHIJKL"[now.month - 1]

IN = "inbound/"
PASS = "pass/"
FAIL = "fail/"


def get_gppractice_out_path(filename_no_ext):
    file_out_path = os.path.join(gettempdir(), f"{filename_no_ext}.{month}{day}A")
    return file_out_path


@step("connect and trigger lambda LR-02")
def connect_to_lambda_lr02_with_valid_payload():
    client = dev.client("lambda", REGION_NAME)
    payload_file = "LR_02_Lambda_Payload.txt"
    payload_temp = os.path.join(DATA, payload_file)

    with open(payload_temp) as jsonfile:
        payload_dict = json.load(jsonfile)

    lr_02_response = client.invoke(
        FunctionName=LR_02_LAMBDA_ARN,
        InvocationType="Event",
        Payload=json.dumps(payload_dict),
    )

    return lr_02_response


@step("connect and trigger lambda LR-02 with invalid payload")
def connect_to_lambda_lr02_with_invalid_payload():
    client = dev.client("lambda", REGION_NAME)
    payload_file = "LR_02_Lambda_Invalid_Payload.txt"
    payload_temp = os.path.join(DATA, payload_file)

    with open(payload_temp) as jsonfile:
        payload_dict = json.load(jsonfile)

    lr_02_response = client.invoke(
        FunctionName=LR_02_LAMBDA_ARN,
        InvocationType="Event",
        Payload=json.dumps(payload_dict),
    )

    return lr_02_response


@step("trigger lambda LR-02 and assert response status code is <StatusCode>")
def assert_lambda_lr_02_response_statuscode(expstatuscode):
    lr_02_response = connect_to_lambda_lr02_with_invalid_payload()

    for key, value in lr_02_response.items():
        print(key, value)
        if key == "StatusCode":
            assert value == int(expstatuscode)


@step("trigger lambda LR-02  and assert responsemetadata HTTPStatusCode response is <StatusCode>")
def assert_lambda_lr_02_response_metadata_httpstatuscode(expstatuscode):
    lr_02_response = connect_to_lambda_lr02_with_invalid_payload()

    for key in lr_02_response.items():
        if key == "ResponseMetadata":
            assert lr_02_response["ResponseMetadata"]["HTTPStatusCode"] == int(expstatuscode)


@step("create gpextract file")
def create_gp_file(testfile, row, invalid_item=None, field_loc=None):
    path = os.path.join(DATA, testfile)
    dir_, filename = os.path.split(path)
    filename_no_ext, ext = os.path.splitext(filename)
    file_out_path = get_gppractice_out_path(filename_no_ext)

    with open(path) as infile:
        in_text = infile.readlines()
        out_lines = []
        ldate = now.strftime("%Y%m%d")
        ltime = now.strftime("%H%M")

    for line in in_text:
        if line.startswith(row) and row == "DOW~1":
            split_line = line.split("~")
            if invalid_item and field_loc:
                split_line[int(field_loc)] = invalid_item
                if field_loc != "4":
                    split_line[4] = ldate
                    split_line[5] = ltime
            elif (invalid_item and field_loc) == None:
                split_line[4] = ldate
                split_line[5] = ltime
            line = "~".join(split_line)

        elif line.startswith(row) and row == "DOW~2":
            split_line = line.split("~")
            split_line[int(field_loc)] = invalid_item
            line = "~".join(split_line)

        out_lines.append(line)

    with open(path) as infile, open(file_out_path, "w") as outfile:
        outfile.writelines(out_lines)
    return file_out_path


@step("connect to s3 and upload gpfile file <testfile> for successful file validation")
def upload_gpextract_file_into_s3(testfile):
    row = "DOW~1"
    temp_destdir = create_gp_file(testfile, row)

    global destination_filename
    destination_filename = os.path.basename(temp_destdir)

    s3 = dev.client("s3", REGION_NAME)
    try:
        s3.upload_file(temp_destdir, LR_01_BUCKET, InputFolderType.IN.value + destination_filename)
        Messages.write_message("Upload Successful")
    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step(
    "connect to s3 and upload gp file with invalid item <invalid_item> in row <row1> at position <fieldlc>"
)
def upload_gpextract_file_into_s3_with_invalid_item(invalid_item, row, fieldlc):
    testfile = "A82023_GPR4LNA1.EIA"
    temp_destdir = create_gp_file(testfile, row, invalid_item, fieldlc)

    global destination_filename
    destination_filename = os.path.basename(temp_destdir)

    s3 = dev.client("s3", REGION_NAME)
    try:
        s3.upload_file(temp_destdir, LR_01_BUCKET, InputFolderType.IN.value + destination_filename)
        Messages.write_message("Upload Successful")
    
    except FileNotFoundError:
        Messages.write_message("File not found")
        raise
    
    return temp_destdir, destination_filename


@step("connect to s3 failed folder and assert failure message <search_word>")
def readfile_in_s3_failed_invalid_item(search_word):
    s3 = dev.client("s3", REGION_NAME)
    fail_prefix = InputFolderType.FAIL.value + destination_filename + "_LOG.txt"
    use_waiters_check_object_exists(LR_01_BUCKET, fail_prefix)
    
    result = s3.list_objects(
        Bucket=LR_01_BUCKET, Prefix=fail_prefix
    )
    

    if result:
        for o in result.get("Contents"):
            data = s3.get_object(Bucket=LR_01_BUCKET, Key=o.get("Key"))
            contents = data["Body"].read().decode("utf-8").splitlines()
            len_content = len(contents)
            actual_line = []
            line_num = 0
            val = 0

            for line in contents:
                actual_line.append(line)
                actual_key = actual_line[line_num]

                if search_word in actual_key:
                    Messages.write_message(
                        "Actual validation error messagein is :" + str(actual_key)
                    )
                    Messages.write_message("row validation successful")
                    val += 1
                    assert search_word in actual_key

                if line_num != len_content or line == "DOW file contains invalid records:":
                    line_num += 1

            if val == 0:
                Messages.write_message("Actual value was :" + str(actual_key))
                assert val, "No value found"


@step("connect to pass folder and check if it has loaded the test file")
def assert_fileloaded_in_s3_pass_folder():
    s3 = dev.client("s3", REGION_NAME)
    expected_filename = InputFolderType.PASS.value + destination_filename
    use_waiters_check_object_exists(LR_01_BUCKET, expected_filename)

    result = s3.list_objects(Bucket=LR_01_BUCKET, Prefix=expected_filename)
    actual_filename = result.get("Contents", [])[0]["Key"]
    assert expected_filename == actual_filename, "destination file not found"
