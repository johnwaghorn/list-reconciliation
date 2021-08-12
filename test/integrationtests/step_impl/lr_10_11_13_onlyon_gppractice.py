from .lr_beforehooks import use_waiters_check_object_exists
from getgauge.python import step
from getgauge.python import Messages
import boto3
import json
import os
from utils.datetimezone import get_datetime_now
from .lr_03_dynamodb import get_latest_jobid
from .tf_aws_resources import get_terraform_output

REGION_NAME = "eu-west-2"
TEST_DATETIME = get_datetime_now()
LR_10_STATE_FUNCTION_ARN = get_terraform_output("lr_10_sfn_arn")
LR_13_BUCKET = get_terraform_output("lr_13_bucket")
s3 = boto3.client("s3", REGION_NAME)

ROOT = os.path.dirname(os.path.abspath(__file__))
EXPECED_GP_ONLY_DATA = os.path.join(ROOT, "data")


def lr_10_response():
    job_id = get_latest_jobid()
    client = boto3.client("stepfunctions", REGION_NAME)
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
    lr_13_fail_response = s3.list_objects_v2(Bucket=LR_13_BUCKET, Prefix=job_id)
    if "Contents" in lr_13_fail_response:
        for object in lr_13_fail_response["Contents"]:
            use_waiters_check_object_exists(LR_13_BUCKET, object["Key"])

    executionarn = lr_10_response["executionArn"]
    return executionarn, job_id


@step(
    "connect to lr-13 s3 bucket and ensure the gponly csv file produced contains the expected gponly records"
)
def assert_file_in_lr13():
    exp_gponly_datafile = "expected_onlyongp.txt"
    exp_gponly_path = os.path.join(EXPECED_GP_ONLY_DATA, "LR_13/" + exp_gponly_datafile)

    s3 = boto3.client("s3", REGION_NAME)
    result = s3.list_objects(Bucket=LR_13_BUCKET)

    with open(exp_gponly_path, "r") as exp_gponly_datafile:
        exp_gponly_data = sorted(exp_gponly_datafile)
        try:
            gp_file_name = next(
                item["Key"] for item in result["Contents"] if "OnlyOnGP" in item["Key"]
            )
            data = s3.get_object(Bucket=LR_13_BUCKET, Key=gp_file_name)
            act_contents = sorted(data["Body"].read().decode("utf-8").splitlines())
            for line, row in zip(act_contents, exp_gponly_data):

                if row.rstrip() == line:
                    Messages.write_message("Actual row is :" + str(line))
                    Messages.write_message("success : Record as expected")
                else:
                    assert (
                        row.rstrip() == line
                    ), f"Actual row is : {str(line)} Expected was : {row.rstrip()}\nUnsuccessful : Record as expected"

        except StopIteration:
            assert False, "'OnlyOnGP' File not found"
