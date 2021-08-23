from .lr_beforehooks import use_waiters_check_object_exists
from utils import InputFolderType
from getgauge.python import step
from getgauge.python import Messages
from utils.datetimezone import get_datetime_now
from .lr_beforehooks import use_waiters_check_object_exists
from .test_helpers import PDS_API_ENV

import boto3
import json
from tempfile import gettempdir
import os
from datetime import timedelta
from .tf_aws_resources import get_terraform_output

# On github
REGION_NAME = "eu-west-2"
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", PDS_API_ENV)
LR_01_BUCKET = get_terraform_output("lr_01_bucket")
LR_02_LAMBDA_ARN = get_terraform_output("lr_02_lambda_arn")

test_datetime = get_datetime_now()
temp_dir = gettempdir()
now = test_datetime - timedelta(hours=1)
day = "123456789ABCDEFGHIJKLMNOPQRSTUV"[now.day - 1]
month = "ABCDEFGHIJKL"[now.month - 1]

IN = "inbound/"
PASS = "pass/"
FAIL = "fail/logs"


def get_gppractice_out_path(filename_no_ext):
    file_out_path = os.path.join(gettempdir(), f"{filename_no_ext}.{month}{day}A")
    return file_out_path


@step("connect and trigger lambda LR-02 with invalid payload")
def connect_to_lambda_lr02_with_invalid_payload():
    client = boto3.client("lambda", REGION_NAME)
    payload_file = "lr_02/lr_02_Lambda_Invalid_Payload.txt"
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

    s3 = boto3.client("s3", REGION_NAME)
    try:
        s3.upload_file(
            temp_destdir, LR_01_BUCKET, f"{InputFolderType.IN.value}{destination_filename}"
        )
        use_waiters_check_object_exists(
            LR_01_BUCKET, f"{InputFolderType.PASS.value}{destination_filename}"
        )
        Messages.write_message("Upload Successful")

    except FileNotFoundError:
        Messages.write_message("File not found")
        raise


@step(
    "connect to s3 and upload gp file with invalid item <invalid_item> in row <row1> at position <fieldlc>"
)
def upload_gpextract_file_into_s3_with_invalid_item(invalid_item, row, fieldlc):
    testfile = "lr_02/A82023_GPR4LNA1.EIA"
    temp_destdir = create_gp_file(testfile, row, invalid_item, fieldlc)

    global destination_filename
    destination_filename = os.path.basename(temp_destdir)

    s3 = boto3.client("s3", REGION_NAME)
    try:
        s3.upload_file(temp_destdir, LR_01_BUCKET, InputFolderType.IN.value + destination_filename)
        Messages.write_message("Upload Successful")

    except FileNotFoundError:
        Messages.write_message("File not found")
        raise

    return temp_destdir, destination_filename


@step("connect to s3 failed folder and assert failure message <search_word>")
def readfile_in_s3_failed_invalid_item(search_word):
    s3 = boto3.client("s3", REGION_NAME)
    lr_01_fail_response = s3.list_objects_v2(Bucket=LR_01_BUCKET, Prefix="fail")
    if "Contents" in lr_01_fail_response:
        for object in lr_01_fail_response["Contents"]:
            use_waiters_check_object_exists(LR_01_BUCKET, object["Key"])
            if "logs" in object.get("Key"):
                data = s3.get_object(Bucket=LR_01_BUCKET, Key=object.get("Key"))
                contents = data["Body"].read().decode("utf-8").splitlines()
                actual_line = []
                line_num = 0

                for line in contents:
                    actual_line.append(line)
                    actual_key = actual_line[line_num]

                    if search_word in actual_key:
                        Messages.write_message(str(actual_key))
                        Messages.write_message("row validation successful")
                        assert search_word in actual_key
                line_num = line_num + 1


@step("connect to pass folder and check if it has loaded the test file")
def assert_fileloaded_in_s3_pass_folder():
    s3 = boto3.client("s3", REGION_NAME)
    expected_filename = InputFolderType.PASS.value + destination_filename
    use_waiters_check_object_exists(LR_01_BUCKET, expected_filename)

    result = s3.list_objects(Bucket=LR_01_BUCKET, Prefix=expected_filename)

    actual_filename = result.get("Contents", [])[0]["Key"]
    assert expected_filename == actual_filename, "destination file not found"
