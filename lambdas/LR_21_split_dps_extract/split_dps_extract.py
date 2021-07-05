import os
import boto3
import csv
import io

from datetime import timedelta
from collections import defaultdict
from botocore.exceptions import ClientError

from utils.datetimezone import get_datetime_now, localize_date
from utils.logger import LOG, log_dynamodb_error, success, UNHANDLED_ERROR

INPUT_BUCKET = os.environ.get("LR_20_SUPPLEMENTARY_INPUT_BUCKET")
OUTPUT_BUCKET = os.environ.get("LR_22_SUPPLEMENTARY_OUTPUT_BUCKET")


class InvalidDSAFile(Exception):
    pass


def lambda_handler(event, context):    
    try:
        upload_key = event["Records"][0]["s3"]["object"]["key"]

        return split_dps_extract(upload_key)

    except Exception as err:
        msg = f"Unhandled error when processing supplementary data file in LR-21"
        error_response = log_dynamodb_error(
            "99999999-2121-2121-2121-999999999999", UNHANDLED_ERROR, msg
        )

        raise Exception(error_response) from err


def split_dps_extract(upload_key: str) -> success:
    """Splits a DPS supplementary file into multiple smaller files by practice

    Args:
        upload_key (str): A path to the s3 file key object

    Returns:
        success: A dict result containing a status and message
    """

    records = read_file(upload_key)
    LOG.info("Data lines extracted")

    per_registered_gp = split_file(upload_key, records)
    LOG.info("Dictionary created for each registered GP")

    write_files(per_registered_gp)
    LOG.info("Output files for each registered GP was successful")

    cleanup_files(upload_key, per_registered_gp)
    LOG.info("Outdated GP file cleanup was successful")

    return success(f"LR-21 processed Supplementary data successfully, from file: {upload_key}")


def read_file(upload_key: str) -> list:
    """Retrieve and read supplementary file data

    Args:
        upload_key (str): A path to the s3 file key object

    Returns:
        list: A list of strings containing file data
    """

    try:
        client = boto3.client("s3")

        file_obj = client.get_object(Bucket=INPUT_BUCKET, Key=upload_key)

        file_data = file_obj["Body"].read().decode("utf-8").splitlines()

        return file_data

    except (ClientError, UnicodeDecodeError) as err:
        msg = f"LR-21 failed to read supplementary data from: {upload_key}"
        error_response = log_dynamodb_error(
            "99999999-2121-2121-2121-999999999999", "HANDLED_ERROR", msg
        )

        raise InvalidDSAFile(error_response) from err


def split_file(upload_key: str, file_data: list) -> dict:
    """Split file data into a dict for each registered GP

    Args:
        upload_key (str): A path to the s3 file key object
        file_data (list): A list of strings containing file data

    Returns:
        dict: A dict of registered GP's
    """

    try:
        per_registered_gp = defaultdict(list)

        reader = csv.reader(file_data)

        next(reader, None)

        for nhs_number, gp_code, disp_flag in reader:
            per_registered_gp[gp_code.strip()].append(
                {"nhs_number": nhs_number.strip(), "dispensing_flag": int(disp_flag)}
            )

        return dict(per_registered_gp)

    except ValueError as err:
        msg = f"LR-21 failed to process file contents for: {upload_key}"
        error_response = log_dynamodb_error(
            "99999999-2121-2121-2121-999999999999", "HANDLED_ERROR", msg
        )

        raise InvalidDSAFile(error_response) from err


def write_files(per_registered_gp: dict):
    """Create and write each GP dict it's own GP file

    Args:
        per_registered_gp (dict): A dict of registered GP's
    """

    client = boto3.client("s3")

    headers = ["nhs_number", "dispensing_flag"]

    for gp, patients in per_registered_gp.items():
        stream = io.StringIO()

        writer = csv.DictWriter(stream, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(patients)

        csv_results_string = stream.getvalue().strip()

        try:
            client.put_object(Body=csv_results_string, Bucket=OUTPUT_BUCKET, Key=f"{gp}.csv")

        except ClientError as err:
            msg = f"Failed to write processed data to output bucket in LR-21"

            error_response = log_dynamodb_error(
                "99999999-2121-2121-2121-999999999999", "HANDLED_ERROR", msg
            )

            raise Exception(error_response) from err


def cleanup_files(upload_key: str, per_registered_gp: dict):
    """Cleanup outdated GP files and clean input bucket

    Args:
        upload_key (str): A path to the s3 file key object
        per_registered_gp (dict): A dict of registered GP's
    """

    client = boto3.client("s3")

    try:
        minimum_last_update = get_datetime_now() - timedelta(hours=4)

        paginator = client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=OUTPUT_BUCKET)

        for page in pages:
            for obj in page["Contents"]:
                mod_date = localize_date(obj['LastModified'])

                if mod_date < minimum_last_update:
                    client.delete_object(Bucket=OUTPUT_BUCKET, Key=obj['Key'])
                    LOG.info(f"Outdated GP data deleted for GP:{str(obj['Key']).replace('.csv', '')}")

        client.delete_object(Bucket=INPUT_BUCKET, Key=upload_key)

    except ClientError as err:
        msg = f"Failed to cleanup files in output bucket in LR-21"
        error_response = log_dynamodb_error(
            "99999999-2121-2121-2121-999999999999", "HANDLED_ERROR", msg
        )

        raise Exception(error_response) from err
