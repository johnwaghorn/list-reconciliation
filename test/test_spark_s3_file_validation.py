from listrec.databricks.matching import (
    get_record_mismatch_summary,
    pds_gp_mismatches,
    output_demographic_mismatches,
)
from listrec.databricks.utils import format_pds_mock_data

import os
import csv
import boto3
import pandas as pd
import pyspark
from io import BytesIO
import numpy as np


ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")

os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"
access_key = os.getenv("AWS_PUBLIC_KEY")
secret_key = os.getenv("AWS_PRIVATE_KEY")

output_bucket = "databricks-poc-nhsdigital"
output_dir = "test/integration"
practice = "B86024"


def test_s3_file_content_match():
    spark = pyspark.sql.SparkSession.builder.getOrCreate()

    with open(os.path.join(DATA, "gp_302.csv")) as infile:
        reader = csv.reader(infile)
        header = next(reader)
        rows = list(reader)

    gp = spark.createDataFrame(
        rows,
        header,
    )

    gp.createOrReplaceTempView("vw_gdppr")

    with open(os.path.join(DATA, "pds_302.csv")) as infile:
        reader = csv.reader(infile)
        header = next(reader)
        rows = list(reader)

    pds = spark.createDataFrame(
        rows,
        header,
    )

    pds = format_pds_mock_data(pds)
    pds.createOrReplaceTempView("vw_pds")

    get_record_mismatch_summary(gp, pds)
    pds_gp_mismatches_df = pds_gp_mismatches(gp, pds)

    output_demographic_mismatches(
        pds_gp_mismatches_df,
        practice,
        output_bucket,
        output_dir,
        access_key,
        secret_key,
        on_databricks=False,
    )

    # expected value
    expected = spark.createDataFrame(
        [
            (
                "2959359119",
                "address",
                "Charing Cross Downtown Oxford Kingston upon Hull",
                "Charing Cross Johnstown Oxford Kingston upon Hull",
            ),
        ],
        ["nhs_number", "item", "gp_value", "pds_value"],
    )

    expected_df = expected.toPandas()
    
    # Defome s3_resorce
    s3_resource = boto3.resource(
        "s3",
        region_name="eu-west-2",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    # get the latest file from the respective location
    objects = list(s3_resource.Bucket(output_bucket).objects.filter(Prefix=output_dir))
    objects.sort(key=lambda o: o.last_modified)
    last_updated_file = objects[-1].key

    # Read tha actual values
    obj = s3_resource.Object(output_bucket, last_updated_file)
    with BytesIO(obj.get()['Body'].read()) as bio:
        act_initial_df = pd.read_csv(bio)

    # Assert
    np.array_equal(act_initial_df, expected_df)
