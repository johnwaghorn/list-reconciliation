from getgauge.python import step
from getgauge.python import Messages
from tempfile import gettempdir
from .tf_aws_resources import get_terraform_output
from utils.datetimezone import get_datetime_now

import boto3
import os
import json

# On github
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)

test_datetime = get_datetime_now()
temp_dir = gettempdir()

REGION_NAME = "eu-west-2"
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
EXPECTED_DATA = os.path.join(ROOT, "data")
LR_23_BUCKET = get_terraform_output("lr_23_bucket")


def update_exp_patient_record_lr23(exp_path, patient_id, job_id):
    with open(exp_path, "r") as infile:
        exp_data = json.load(infile)
        exp_data["system"]["patientId"] = patient_id
        exp_data["system"]["jobId"] = job_id

        with open(exp_path, "w") as outfile:
            json.dump(exp_data, outfile)

        exp_data = sorted(exp_data["differences"], key=lambda x: x["ruleId"])
        return exp_data


@step(
    "connect to <lr_bucket> s3 bucket and ensure patient payload record file with patientid <patientid> is generated as expected <exp_datafile>"
)
def assert_expected_file_in_lr13(lr_bucket, patientid, exp_datafile):
    s3 = dev.client("s3", REGION_NAME)
    result = s3.list_objects(Bucket=LR_23_BUCKET)

    for filename in result.get("Contents"):
        if patientid in filename:
            data = s3.get_object(Bucket=LR_23_BUCKET, Key=filename.get("Key"))
            data_content = data["Body"]
            act_contents = json.loads(data_content.read().decode("utf-8"))

            patient_id = act_contents["system"]["patientId"]
            job_id = act_contents["system"]["jobId"]

            exp_path = os.path.join(EXPECTED_DATA, lr_bucket + exp_datafile)
            exp_data = json.dumps(
                update_exp_patient_record_lr23(exp_path, patient_id, job_id), indent=4
            )

            act_contents = sorted(act_contents["differences"], key=lambda x: x["ruleId"])
            act_content = json.dumps(act_contents, indent=4)
            assert (
                act_content == exp_data
            ), f"Actual content is : {act_content} Expected was : {exp_data}\nUnsuccessful : expected record not found"
