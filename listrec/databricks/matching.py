from datetime import datetime
from pathlib import Path

import os

from pyspark.sql.functions import col

import pyspark

from listrec.databricks.utils import save_to_csv, upload_to_s3


spark = pyspark.sql.SparkSession.builder.config(
    "spark.driver.bindAddress", "127.0.0.1"
).getOrCreate()


def get_pds_records_status(
    gp: pyspark.sql.DataFrame, pds: pyspark.sql.DataFrame, sex_lkp: pyspark.sql.DataFrame
) -> pyspark.sql.DataFrame:
    """Create a dataframe containing PDS record mismatch details.

    Args:
        gp (pyspark.sql.DataFrame): GDPPR dataframe.
        pds (pyspark.sql.DataFrame): PDS dataframe.
        sex_lkp (pyspark.sql.DataFrame): Sex lookup dataframe.

    Returns:
        pyspark.sql.DataFrame
    """
    gp.createOrReplaceTempView("gp_vw")
    pds.createOrReplaceTempView("pds_vw")
    sex_lkp.createOrReplaceTempView("sex_lkp_vw")

    df = spark.sql(
        f"""
        SELECT
            pds.name.familyName `SURNAME`,
            concat_ws(' ', pds.name.givenNames[0], pds.name.givenNames[1], pds.name.givenNames[2], pds.name.givenNames[3]) `FORENAMES`,
            date_format(to_date(cast(pds.date_of_birth as string), 'yyyyMMdd'), 'dd/MM/yyyy') `DOB`,
            pds.nhs_number `NHS NO.`,
            pds.gp.code `PRACTICE`,
            pds.address.lines[0] `ADD 1`,
            pds.address.lines[1] `ADD 2`,
            pds.address.lines[2] `ADD 3`,
            pds.address.lines[3] `ADD 4`,
            pds.address.lines[4] `ADD 5`,
            pds.address.postcode `POSTCODE`,
            s.sex AS `SEX`,
            date_format(to_date(cast(pds.gp.from as string), 'yyyyMMdd'), 'dd/MM/yyyy') `DATE_ACCEPT.`
        FROM pds_vw pds
        LEFT JOIN gp_vw GP ON GP.nhs_number = pds.nhs_number
        LEFT JOIN sex_lkp_vw s on pds.gender.gender = s.code
        WHERE pds.nhs_number IS NOT NULL
        AND gp.practice <> pds.gp.code
        OR gp.practice is null
        """
    )

    return df


def output_registration_differences(
    pds_records_status: pyspark.sql.DataFrame,
    gp_practice: str,
    bucket: str,
    directory: Path,
    aws_access_key: str,
    aws_secret_key: str,
):
    """Writes registration differences csv files to an S3 bucket.

    Args:
        pds_records_status (pyspark.sql.DataFrame): PDS registration differences DataFrame.
        gp_practice (str): GP Practice to filter.
        bucket (str): Bucket to save the file to.
        directory (str): Target output directory in bucket. If targeting root, use ''
        access_key (str): AWS public key.
        secret_key (str): AWS private key.
    """

    date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    pds_filename = f"{gp_practice}_OnlyOnPDS_{date}.csv"
    gp_filename = f"{gp_practice}_OnlyOnGP_{date}.csv"

    output_pds_records_status(
        pds_records_status,
        gp_practice,
        bucket,
        os.path.join(directory, pds_filename),
        aws_access_key,
        aws_secret_key,
    )


def output_pds_records_status(
    pds_records_status: pyspark.sql.DataFrame,
    gp_practice: str,
    bucket: str,
    out_path: Path,
    aws_access_key: str,
    aws_secret_key: str,
):
    """Writes PDS registration differences csv files to an S3 bucket.

    Args:
        pds_records_status (pyspark.sql.DataFrame): PDS registration differences DataFrame.
        gp_practice (str): GP Practice to filter.
        bucket (str): Bucket to save the file to.
        out_path (Path): Target output file in bucket.
        access_key (str): AWS public key.
        secret_key (str): AWS private key.
    """
    filename = os.path.basename(out_path)
    df = pds_records_status.filter(col("PRACTICE") == gp_practice).drop(col("PRACTICE"))
    saved_file = save_to_csv(df, filename, on_databricks=True)

    upload_to_s3(saved_file, bucket, out_path, aws_access_key, aws_secret_key)
