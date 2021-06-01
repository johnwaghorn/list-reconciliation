from typing import Dict

import csv
import json
import os

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import boto3
import requests


PDS_API_URL = os.getenv("PDS_API_URL")


class PDSAPIError(Exception):
    pass


def get_mock_pds_record(url: str, nhs_number: str, *args, **kwargs) -> Dict:
    """Get a hardcoded mocked PDS record from a CSV on S3.

    Args:
        url (str): Full S3 url to the file containing mock PDS records.
        nhs_number: 10-digit NHS number of the record to retrieve.

    Returns:
        Dict: Dictionary containing demographics data for comparison.
    """

    bucket_name, *path_list = url.replace("s3://", "").split("/")
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    obj = bucket.Object(key="/".join(path_list))
    response = obj.get()
    lines = response["Body"].read().decode("utf-8").split("\n")

    reader = csv.DictReader(lines)
    for row in reader:
        if row["nhs_number"] == nhs_number:
            return {
                "surname": row["surname"],
                "forenames": row["forename"].split(","),
                "title": row["prefix"].split(","),
                "gender": row["gender"],
                "date_of_birth": row["birthdate"],
                "address": row["address"].split(","),
                "postcode": row["postcode"],
                "gp_code": row["gp"],
                "gp_registered_date": row["gp_registered_date"],
                "is_sensitive": row["display"] in ("restricted", "sensitive"),
            }
    else:
        raise PDSAPIError(f"NHS number {nhs_number} does not exist in mock data")


def get_pds_fhir_record(
    url: str, nhs_number: str, max_retries: int = 5, backoff_factor: int = 1, *args, **kwargs
) -> Dict:
    """Get a PDS record using the FHIR API.

    Args:
        url (str): Full url for the PDS FHIR API.
        nhs_number: 10-digit NHS number of the record to retrieve.
        max_retries (int): Number of retries to attempt.
        backoff_factor (int): Each retry attempt is delayed
            by: {backoff factor} * (2 ** ({number of total retries} - 1))

    Returns:
        Dict: Dictionary containing demographics data for comparison.
    """

    session = requests.Session()
    retries = Retry(total=max_retries, backoff_factor=backoff_factor)
    session.mount("https://", HTTPAdapter(max_retries=retries))

    response = session.get(f"{url}/Patient/{nhs_number}")
    response.raise_for_status()

    content = json.loads(response.content)

    return {
        "surname": content["name"][0]["family"],
        "forenames": content["name"][0]["given"],
        "title": content["name"][0]["prefix"],
        "gender": content["gender"],
        "date_of_birth": content["birthDate"],
        "address": content["address"][0]["line"],
        "postcode": content["address"][0]["postalCode"],
        "gp_code": content["generalPractitioner"][0]["identifier"]["value"],
        "gp_registered_date": content["generalPractitioner"][0]["identifier"]["period"]["start"],
        "is_sensitive": content["meta"]["security"][0]["display"] in ("restricted", "sensitive"),
    }


def get_pds_record(nhs_number, *args, **kwargs):
    if PDS_API_URL.startswith("http"):
        return get_pds_fhir_record(PDS_API_URL, nhs_number, *args, **kwargs)
    elif PDS_API_URL.startswith("s3"):
        return get_mock_pds_record(PDS_API_URL, nhs_number, *args, **kwargs)