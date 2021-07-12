from getgauge.python import step
from getgauge.python import Messages
import boto3
import json
import os
import time
from utils.datetimezone import get_datetime_now
from .lr_03_dynamodb import get_latest_jobid
from .tf_aws_resources import get_aws_resources

# On github
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)


REGION_NAME = "eu-west-2"
TEST_DATETIME = get_datetime_now()
AWS_RESOURCE = get_aws_resources()
LR_10_STATE_FUNCTION_ARN = AWS_RESOURCE["lr_10_sfn_arn"]["value"]
LR_13_BUCKET = AWS_RESOURCE["lr_13_bucket"]["value"]

ROOT = os.path.dirname(os.path.abspath(__file__))
EXPECED_GP_ONLY_DATA = os.path.join(ROOT, "data")


def lr_10_response():
    job_id = get_latest_jobid()
    client = dev.client("stepfunctions", REGION_NAME)
    now = TEST_DATETIME.now()
    time_gen = "%02d%02d%02d%02d%d" % (
        now.year,
        now.month,
        now.day,
        now.minute,
        now.second,
    )
    integ_auto_test = "integ_auto_test_" + time_gen
    lr_10_response = client.start_execution(
        stateMachineArn=LR_10_STATE_FUNCTION_ARN,
        name=integ_auto_test,
        input=json.dumps({"job_id": job_id}),
    )
    time.sleep(5)
    executionarn = lr_10_response["executionArn"]
    return executionarn


@step(
    "connect and trigger lr-10 state function for registration differences and assert status succeeded"
)
def connect_statefunc_lr10():
    client = dev.client("stepfunctions", REGION_NAME)
    executionarn = lr_10_response()
    desc_exec_resp = client.describe_execution(executionArn=executionarn)
    status = desc_exec_resp["status"]

    while status != "SUCCEEDED":
        if status == "FAILED":
            Messages.write_message("LR 10 StepFunction failed")
            Messages.write_message(status)
            Messages.write_message(desc_exec_resp)
            Messages.write_message(executionarn)
            assert False
        else:
            desc_exec_resp = client.describe_execution(executionArn=executionarn)
            status = desc_exec_resp["status"]


@step("connect to s3 bucket and ensure the csv file produced contains the expected gponly record")
def assert_file_in_lr13():
    exp_gponly_datafile = "expected_onlyongp.txt"
    exp_gponly_path = os.path.join(EXPECED_GP_ONLY_DATA, "LR_13/" + exp_gponly_datafile)

    s3 = dev.client("s3", REGION_NAME)
    result = s3.list_objects(Bucket=LR_13_BUCKET)
    with open(exp_gponly_path, "r") as exp_gponly_datafile:
        exp_gponly_data = sorted(exp_gponly_datafile)

        if result.get("Contents") != None:
            for key_items in result.get("Contents"):
                for filename in key_items.items():
                    if "tbc-OnlyOnGP" in str(filename):
                        data = s3.get_object(Bucket=LR_13_BUCKET, Key=key_items.get("Key"))
                        act_contents = sorted(data["Body"].read().decode("utf-8").splitlines())
                        for line, row in zip(act_contents, exp_gponly_data):

                            if row.rstrip() == line:
                                Messages.write_message("Actual row is :" + str(line))
                                Messages.write_message("success : Record as expected")
                            else:
                                assert (
                                    row.rstrip() == line
                                ), f"Actual row is : {str(line)} Expected was : {row.rstrip()}\nUnsuccessful : Record as expected"
