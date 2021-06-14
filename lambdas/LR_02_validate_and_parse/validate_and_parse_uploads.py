import boto3
import json
import os

from botocore.exceptions import ClientError
from datetime import datetime

from gp_file_parser.file_name_parser import InvalidFilename
from gp_file_parser.parser import (
    InvalidGPExtract,
    parse_gp_extract_file_s3,
    handle_invalid_extract,
    process_invalid_message,
    INBOUND_PREFIX,
    PASSED_PREFIX,
    LOG,
)
from utils import write_to_mem_csv

ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
SESSION_TOKEN = os.environ.get("AWS_SESSION_TOKEN")

REGISTRATION_EXTRACT_BUCKET = os.environ.get("AWS_S3_REGISTRATION_EXTRACT_BUCKET")


def validate_and_parse_uploads(event, context):
    """Handler to process and validate an uploaded S3 object containing a GP flat
    file extract

    Args:
        event: S3 ObjectCreated event
        context: Lambda context object
    """
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            aws_session_token=SESSION_TOKEN,
        )

        upload_key = event["Records"][0]["s3"]["object"]["key"]
        upload_filename = upload_key.replace(INBOUND_PREFIX, "")

        LOG.info(f"{upload_key} validation process begun")

        results = parse_gp_extract_file_s3(
            ACCESS_KEY,
            SECRET_KEY,
            SESSION_TOKEN,
            REGISTRATION_EXTRACT_BUCKET,
            upload_key,
            datetime.now(),
        )

        invalid_records = [r for r in results if "_INVALID_" in list(r.keys())]

        if invalid_records:
            raise InvalidGPExtract(json.dumps(invalid_records))

    except KeyError:
        raise KeyError("Could not access file upload key from lambda event")

    except ClientError:
        raise ClientError

    except (AssertionError, InvalidGPExtract, InvalidFilename) as err:
        LOG.error(f"{err}: Beginning invalid file handling process for '{upload_filename}'")

        try:
            message = process_invalid_message(err)

            handle_invalid_extract(
                ACCESS_KEY,
                SECRET_KEY,
                SESSION_TOKEN,
                REGISTRATION_EXTRACT_BUCKET,
                upload_key,
                message,
            )

            LOG.info(f"Successfully handled invalid file: {upload_filename}")

        except Exception as err:
            LOG.error(f"{err} Could not handle invalid file: {upload_filename}")
            raise err

    else:
        LOG.info(f"{upload_filename} results collected, parsing {len(results)} records")

        try:
            stream = write_to_mem_csv(results, list(results[0].keys()))

            csv_results_string = stream.getvalue()

        except Exception as err:
            LOG.error(f"{err}: Failed to parse records dict")
            raise err

        else:
            passed_filename = upload_filename + ".csv"
            passed_key = PASSED_PREFIX + passed_filename

            s3_client.put_object(
                Body=csv_results_string, Bucket=REGISTRATION_EXTRACT_BUCKET, Key=passed_key
            )

            s3_client.delete_object(Bucket=REGISTRATION_EXTRACT_BUCKET, Key=upload_key)

            LOG.info(f"{passed_filename} processed sucessfully")
