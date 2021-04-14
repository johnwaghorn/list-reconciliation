from datetime import datetime
from pathlib import Path

import os

from pyspark.sql.functions import to_date, col, concat_ws, udf, lit
from pyspark.sql.types import StringType

import pyspark

from listrec.databricks.utils import blank_as_null, save_to_csv, upload_to_s3
from listrec.databricks.comparison_utils.compare_name import compare_patient_name


ACTION_COLUMN = "action"
ACTION_REQUIRES_VALIDATION = "Further validation required"


spark = pyspark.sql.SparkSession.builder.config(
    "spark.driver.bindAddress", "127.0.0.1"
).getOrCreate()


def compare_gp_pds_date_of_birth(
    gp_pds_df: pyspark.sql.DataFrame, gp_col: pyspark.sql.Column, pds_col: pyspark.sql.Column
) -> pyspark.sql.DataFrame:
    """Check date of birth differences between PDS and GP data and flag records
    for further action, creating a dataframe.

    Args:
        gp_pds_df (pyspark.sql.DataFrame): Dataframe containing GP and PDS
            records joined on NHS number
        gp_col (pyspark.sql.Column): Column from GP data for date of birth.
        pds_col (pyspark.sql.Column): Column from GP data for date of birth.

    Returns:
        pyspark.sql.DataFrame: Dataframe containing only records where the date of birth
            is different, with a further action flag
    """
    return (
        gp_pds_df.filter(gp_col != pds_col)
        .withColumn(ACTION_COLUMN, lit(ACTION_REQUIRES_VALIDATION))
        .withColumn("item", lit("date_of_birth"))
        .select(
            "practice",
            "nhs_number",
            "item",
            col("date_of_birth").alias("gp_value"),
            col("pds_date_of_birth").alias("pds_value"),
            ACTION_COLUMN,
        )
    )


def compare_gp_pds_names(
    gp_pds_df: pyspark.sql.DataFrame,
    gp_surname: pyspark.sql.Column,
    pds_surname: pyspark.sql.Column,
    gp_forenames: pyspark.sql.Column,
    pds_forenames: pyspark.sql.Column,
) -> pyspark.sql.DataFrame:
    """Check for name differences between PDS and GP data and flag records
    for further action, creating a dataframe.

    Args:
        gp_pds_df (pyspark.sql.DataFrame): Dataframe containing GP and PDS
            records joined on NHS number
        gp_surname (pyspark.sql.Column): GP surname column.
        pds_surname (pyspark.sql.Column): PDS surname column.
        gp_forenames (pyspark.sql.Column): GP forename column.
        pds_forenames (pyspark.sql.Column): PDS forename column.
        
    Returns:
        pyspark.sql.DataFrame: Dataframe containing only records where the date of birth
            is different, with a further action flag
    """

    udf_compare_patient_name = udf(compare_patient_name, StringType())

    return (
        gp_pds_df.where((gp_surname != pds_surname) | (gp_forenames != pds_forenames))
        .withColumn(
            ACTION_COLUMN,
            udf_compare_patient_name(gp_forenames, gp_surname, pds_forenames, pds_surname),
        )
        .withColumn("item", lit("name"))
        .select(
            "practice",
            "nhs_number",
            "item",
            concat_ws(", ", col("surname"), col("forename")).alias("gp_value"),
            concat_ws(", ", col("name.familyName"), col("forenames")).alias("pds_value"),
            ACTION_COLUMN,
        )
    )


def get_record_mismatch_summary(
    gp_df: pyspark.sql.DataFrame, pds_df: pyspark.sql.DataFrame
) -> pyspark.sql.DataFrame:
    """Create a dataframe containing summary of record mismatches between PDS and GDPPR.

    Args:
        gp_df (pyspark.sql.DataFrame): GP Practice dataframe.
        pds_df (pyspark.sql.DataFrame): PDS dataframe.

    Returns:
        pyspark.sql.DataFrame
    """

    pds = (
        pds_df.withColumn("dob", to_date(col("date_of_birth").cast("string"), "yyyyMMdd"))
        .drop("date_of_birth")
        .withColumn(
            "address_lines",
            concat_ws(
                " ",
                col("address.lines").getItem(0),
                col("address.lines").getItem(1),
                col("address.lines").getItem(2),
                col("address.lines").getItem(3),
                col("address.lines").getItem(4),
            ),
        )
    ).withColumn(
        "forenames",
        concat_ws(
            " ",
            col("name.givenNames").getItem(0),
            col("name.givenNames").getItem(1),
            col("name.givenNames").getItem(2),
            col("name.givenNames").getItem(3),
            col("name.givenNames").getItem(4),
        ),
    )

    gp_df = gp_df.withColumn(
        "gp_address",
        concat_ws(
            " ",
            blank_as_null("address_1"),
            blank_as_null("address_2"),
            blank_as_null("address_3"),
            blank_as_null("address_4"),
            blank_as_null("address_5"),
        ),
    ).drop("address")

    gp_df.createOrReplaceTempView("gp_vw")
    pds.createOrReplaceTempView("pds_vw")
    
    # Get count of records per practice, total
    gdppr_counts = spark.sql(
        """
        SELECT
            COALESCE(g.practice, p.gp.code) AS practice,
            GREATEST(COUNT(g.practice), COUNT(p.gp.code)) AS total
        FROM gp_vw g
        JOIN pds_vw p
            ON g.practice = p.gp.code
            AND p.nhs_number = g.nhs_number
        GROUP BY g.practice, p.gp.code
        """
    )

    # Create counts table for full matches between GP and PDS
    gp_match_counts = spark.sql(
        """
        SELECT
            COALESCE(g.practice, p.gp.code) AS practice,
            GREATEST(COUNT(g.practice), COUNT(p.gp.code)) AS same
        FROM gp_vw g
        INNER JOIN pds_vw p ON
            g.nhs_number = p.nhs_number
            AND g.practice = p.gp.code
        WHERE
            g.Date_of_Birth = dob
            AND g.SURNAME = p.name.familyName
            AND g.FORENAME = p.forenames
            AND g.sex = p.gender.gender
            AND g.gp_address = p.address_lines
            AND g.postcode = p.address.postcode
        GROUP BY g.practice, p.gp.code
        """
    )

    gpes_pds_match_stats = gdppr_counts.join(gp_match_counts, "practice", how="inner").withColumn(
        "diffs", col("total") - col("same")
    )

    return gpes_pds_match_stats


def pds_gp_mismatches(
    gp_df: pyspark.sql.DataFrame, pds_df: pyspark.sql.DataFrame
) -> pyspark.sql.DataFrame:
    """Generate a GP-PDS mismatches dataframe.
    Args:
        gp_df (pyspark.sql.DataFrame): GP Practice dataframe.
        pds_df (pyspark.sql.DataFrame): PDS dataframe.

    Returns:
        pyspark.sql.DataFrame
    """
    
    pds_df = (
        pds_df.withColumn("pds_date_of_birth", col("date_of_birth"))
        .drop("date_of_birth")
        .withColumn(
            "address_lines",
            concat_ws(
                " ",
                col("address.lines").getItem(0),
                col("address.lines").getItem(1),
                col("address.lines").getItem(2),
                col("address.lines").getItem(3),
                col("address.lines").getItem(4),
            ),
        )
    ).withColumn(
        "forenames",
        concat_ws(
            " ",
            col("name.givenNames").getItem(0),
            col("name.givenNames").getItem(1),
            col("name.givenNames").getItem(2),
            col("name.givenNames").getItem(3),
            col("name.givenNames").getItem(4),
        ),
    )
    
    gp_df = gp_df.withColumn(
        "gp_address",
        concat_ws(
            " ",
            blank_as_null("address_1"),
            blank_as_null("address_2"),
            blank_as_null("address_3"),
            blank_as_null("address_4"),
            blank_as_null("address_5"),
        ),
    ).drop("address")

    gp_pds_df = gp_df.join(pds_df, on="nhs_number", how="inner")

    date_of_birth = compare_gp_pds_date_of_birth(
        gp_pds_df,
        col("date_of_birth"),
        to_date(col("pds_date_of_birth").cast("string"), "yyyyMMdd"),
    )
    date_of_birth.createOrReplaceTempView("vw_date_of_birth")

    name = compare_gp_pds_names(
        gp_pds_df, col("surname"), col("name.familyName"), col("forename"), col("forenames")
    )
    name.createOrReplaceTempView("vw_name")

    sex = gp_pds_df.filter(col("sex") != col("gender.gender"))
    sex.createOrReplaceTempView("vw_sex")

    address_2 = gp_pds_df.filter(col("gp_address") != col("address_lines"))
    address_2.createOrReplaceTempView("vw_address")

    postcode = gp_pds_df.filter(col("postcode") != col("address.postcode"))
    postcode.createOrReplaceTempView("vw_postcode")

    gp_mismatched_data = spark.sql(
        """
        SELECT
            practice,
            nhs_number,
            item,
            gp_value,
            pds_value, 
            action AS action
        FROM vw_name
        UNION
        SELECT
            practice,
            nhs_number,
            item,
            gp_value,
            pds_value,
            action AS action
        FROM vw_date_of_birth
        UNION
        SELECT
            practice,
            nhs_number,
            'sex' AS item,
            sex AS gp_value,
            gender.gender AS pds_value,
            null AS action            
        FROM vw_sex
        UNION
        SELECT
            practice,
            nhs_number,
            'address' AS item,
            gp_address AS gp_value,
            address_lines AS pds_value,
            null AS action
        FROM vw_address
        UNION
        SELECT
            practice,
            nhs_number,
            'postcode' AS item,
            postcode AS gp_value,
            address.postcode AS pds_value,
            null AS action
        FROM vw_postcode
        """
    ).orderBy(["practice", "nhs_number"])

    return gp_mismatched_data


def get_pds_records_status(
    gp: pyspark.sql.DataFrame, pds: pyspark.sql.DataFrame, sex_lkp: pyspark.sql.DataFrame
) -> pyspark.sql.DataFrame:
    """Create a dataframe containing PDS record mismatch details.

    Args:
        gp (pyspark.sql.DataFrame): GDPPR dataframe.
        pds (pyspark.sql.DataFrame): PDS dataframe.

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
            CONCAT_WS(' ', pds.name.givenNames[0], pds.name.givenNames[1], pds.name.givenNames[2], pds.name.givenNames[3]) `FORENAMES`,
            DATE_FORMAT(TO_DATE(CAST(pds.date_of_birth AS STRING), 'yyyyMMdd'), 'dd/MM/yyyy') `DOB`,
            pds.nhs_number `NHS NO.`,
            pds.gp.code `PRACTICE`,
            pds.address.lines[0] `ADD 1`,
            pds.address.lines[1] `ADD 2`,
            pds.address.lines[2] `ADD 3`,
            pds.address.lines[3] `ADD 4`,
            pds.address.lines[4] `ADD 5`,
            pds.address.postcode `POSTCODE`,
            s.sex AS `SEX`,
            DATE_FORMAT(TO_DATE(CAST(pds.gp.from as string), 'yyyyMMdd'), 'dd/MM/yyyy') `DATE_ACCEPT.`
        FROM pds_vw pds
        LEFT JOIN gp_vw GP ON GP.nhs_number = pds.nhs_number
        LEFT JOIN sex_lkp_vw s ON pds.gender.gender = s.code
        WHERE pds.nhs_number IS NOT NULL
        AND gp.practice <> pds.gp.code
        OR gp.practice IS NULL
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
        aws_access_key (str): AWS public key.
        aws_secret_key (str): AWS private key.
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


def output_demographic_mismatches(
    demographic_mismatches: pyspark.sql.DataFrame,
    gp_practice: str,
    bucket: str,
    directory: Path,
    aws_access_key: str,
    aws_secret_key: str,
):
    """Writes demographic differences csv files to an S3 bucket.

    Args:
        demographic_mismatches (pyspark.sql.DataFrame): Demographic differences DataFrame.
        gp_practice (str): GP Practice to filter.
        bucket (str): Bucket to save the file to.
        directory (str): Target output directory in bucket. If targeting root, use ''
        aws_access_key (str): AWS public key.
        aws_secret_key (str): AWS private key.
    """

    date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    mismatch_filename = f"{gp_practice}_Mismatch_{date}.csv"

    df = demographic_mismatches.filter(col("PRACTICE") == gp_practice).drop(col("PRACTICE"))
    saved_file = save_to_csv(df, mismatch_filename, on_databricks=True)

    upload_to_s3(
        saved_file,
        bucket,
        os.path.join(directory, mismatch_filename),
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
        aws_access_key (str): AWS public key.
        aws_secret_key (str): AWS private key.
    """
    filename = os.path.basename(out_path)
    df = pds_records_status.filter(col("PRACTICE") == gp_practice).drop(col("PRACTICE"))
    saved_file = save_to_csv(df, filename, on_databricks=True)

    upload_to_s3(saved_file, bucket, out_path, aws_access_key, aws_secret_key)
