from getgauge.python import step
from .tf_aws_resources import get_aws_resources
import boto3
import os

access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")
dev = boto3.session.Session(access_key, secret_key)

aws_resource = get_aws_resources()
JOBS_TABLE = aws_resource["jobs_table"]["value"]


@step("connect to lr-03 dynamodb and get the latest JobId for a gppractice file")
def get_latest_jobid():
    dev1 = dev.resource("dynamodb", region_name="eu-west-2")
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
