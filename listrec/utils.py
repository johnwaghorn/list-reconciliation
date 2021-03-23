import os
import shutil

from pathlib import Path
from uuid import uuid4

import boto3
import pyspark


def upload_to_s3(path: Path, bucket: str, filename: str, access_key: str, secret_key: str):
    """Upload a file to an S3 bucket.

    Args:
        path (Path): Path to file to upload.
        bucket (str): Bucket to save the file to.
        filename (str): Target filename, including full path within bucket if required.
        access_key (str): AWS public key.
        secret_key (str): AWS private key.
    """

    s3 = boto3.resource(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    s3.Object(bucket, filename).put(Body=open(path).read())


def save_to_csv(
    dataframe: pyspark.sql.DataFrame, filename: str, on_databricks: bool = False
) -> Path:
    """Save a dataframe to CSV file.

    Args:
        dataframe (pyspark.sql.DataFrame): Pyspark DataFrame.
        filename (str): Target filename.
        on_databricks (bool): Set to True if this is running on databricks, to account for
            manipulation of file save locations.

    Returns:
        Path: Path to output file.
    """

    # Databricks saves to the /dbfs/ directory by default so handle it here
    # for manual operations
    if on_databricks:
        databricks_filename = f"/dbfs/{filename.strip('/')}"
        temp_filename = (
            f"/dbfs/{os.path.dirname(filename.strip('/'))}/{uuid4()}_{os.path.basename(filename)}"
        )
    else:
        databricks_filename = filename
        temp_filename = os.path.join(
            os.path.dirname(filename), f"{uuid4()}_{os.path.basename(filename)}"
        )

    try:
        shutil.rmtree(databricks_filename)
    except:
        pass

    try:
        os.remove(databricks_filename)
    except:
        pass
    # coalesce(1) creates a single output csv file
    dataframe.coalesce(1).write.format("csv").save(filename, header="true")

    part_file = [f for f in os.listdir(databricks_filename) if f.startswith("part")][0]

    os.rename(os.path.join(databricks_filename, part_file), temp_filename)
    shutil.rmtree(databricks_filename)
    os.rename(temp_filename, databricks_filename)

    return os.path.abspath(databricks_filename)
