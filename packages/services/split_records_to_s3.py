from typing import List

import json
import os

import boto3

from utils import chunk_list

# 128kb max Event payload size, minus enough to allow for job_id and practice_code in the body
PAYLOAD_SIZE = (128 * 1024) - 200


def split_records_to_s3(
    records: List[str],
    id_cols: List[str],
    destination_bucket: str,
    source: str,
    max_size: int = 128 * 1024,
):
    """Splits a list of JSON objects into multiple single files, each containing a single JSON
    object. Payload size to trigger the AWS lambda is optional, and defaults to 128kb, minus the
    bytes needed for the json property names.

    Args:
        records (List[str]): List of JSON objects.
        id_cols (List[str]): List of one or more columns present in each record in `records`
            which can be used to generate a compound ID.
        destination_bucket (str): S3 bucket to output JSON files to.
        source (str): Label to identify the source of the files and to facilitate logging.
        max_size (int, optional): Max payload size, default: 128kb max Lambda Event payload size.
    """

    def utf8len(x):
        return len(x.encode("utf-8"))

    lambda_ = boto3.client("lambda", region_name=os.getenv("AWS_REGION"))

    reserved_len = utf8len(
        json.dumps({"records": "", "destination_bucket": "", "id_cols": "", "source": ""})
    )

    chunks = chunk_list(records, max_size - reserved_len, utf8len)

    for chunk in chunks:
        body = {
            "records": chunk,
            "destination_bucket": destination_bucket,
            "id_cols": id_cols,
            "source": source,
        }

        lambda_.invoke(
            FunctionName=os.getenv("LR_24_SAVE_RECORDS_TO_S3"),
            InvocationType="Event",
            Payload=json.dumps(body),
        )
