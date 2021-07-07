from getgauge.python import step, Messages
from .tf_aws_resources import get_aws_resources
import boto3
import os

# On github
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)

REGION_NAME = "eu-west-2"
AWS_RESOURCE = get_aws_resources()
JOBS_TABLE = AWS_RESOURCE["jobs_table"]["value"]
INFLIGHT_TABLE = AWS_RESOURCE["inflight_table"]["value"]


@step("connect to lr-03 dynamodb and get the latest JobId for a gppractice file")
def get_latest_jobid():
    dev1 = dev.resource("dynamodb", REGION_NAME)
    job_table = dev1.Table(JOBS_TABLE)
    job_data = job_table.scan()
    job_items = []
    for key, value in job_data.items():
        if key == "Items":
            job_items = [j for j in value]
            job_items = sorted(job_items, reverse=True, key=lambda i: i["Timestamp"])
            if job_items:
                latest_job_id = job_items[0]
                return latest_job_id["Id"]


@step("get InFlight table item count")
def get_inflight_table_itemcount():
    dev1 = dev.resource("dynamodb", region_name="eu-west-2")
    inflight_table = dev1.Table(INFLIGHT_TABLE)
    inflight_data = inflight_table.scan()
    print(inflight_data)
    for key, value in inflight_data.items():
        if key == "Count" and value == 0:
            Messages.write_message("inflight table count is :" + str(value))
