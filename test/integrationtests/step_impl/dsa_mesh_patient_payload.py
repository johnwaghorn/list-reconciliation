import json
import os
from tempfile import gettempdir

import boto3
from getgauge.python import step

from .test_helpers import PDS_API_ENV
from .tf_aws_resources import get_terraform_output
from datetime import datetime

test_datetime = datetime.now()
temp_dir = gettempdir()

REGION_NAME = "eu-west-2"
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", PDS_API_ENV)
MESH_BUCKET = get_terraform_output("mesh_bucket")
OUTBOUND_INTERNALSPINE = "outbound_X26OT178TEST_to_INTERNALSPINE"

s3 = boto3.client("s3", REGION_NAME)


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
    "connect to MESH bucket and ensure patient payload record file with patientid <patientid> is generated as expected <exp_datafile>"
)
def assert_expected_file_in_mesh_bucket(patientid, exp_datafile):
    result = s3.list_objects(Bucket=MESH_BUCKET)
    for filename in result.get("Contents"):
        if OUTBOUND_INTERNALSPINE in filename.get("Key") and patientid in filename.get("Key"):
            data = s3.get_object(Bucket=MESH_BUCKET, Key=filename.get("Key"))
            data_content = data["Body"]
            act_contents = json.loads(data_content.read().decode("utf-8"))

            patient_id = act_contents["system"]["patientId"]
            job_id = act_contents["system"]["jobId"]

            exp_path = os.path.join(DATA, "mesh", exp_datafile)
            exp_data = json.dumps(
                update_exp_patient_record_lr23(exp_path, patient_id, job_id), indent=4
            )

            act_contents = sorted(act_contents["differences"], key=lambda x: x["ruleId"])
            act_content = json.dumps(act_contents, indent=4)
            assert (
                act_content == exp_data
            ), f"Actual content is : {act_content} Expected was : {exp_data}\nUnsuccessful : expected record not found"
