import os
import pyspark

from datetime import datetime
from pathlib import Path
from pyspark.sql.functions import to_date, col, concat_ws, udf, lit
from pyspark.sql.types import StringType, ArrayType

from listrec.databricks.comparison_utils.compare_name import (
    compare_patient_name,
    ACTION_REQUIRES_VALIDATION,
    FORENAME,
    SURNAME,
    BOTH_NAMES,
)

from listrec.databricks.utils import (
    blank_as_null,
    save_to_csv,
    upload_to_s3,
    update_spaces,
    update_caps,
)

ACTION_COLUMN = "action"

spark = pyspark.sql.SparkSession.builder.config(
    "spark.driver.bindAddress", "127.0.0.1"
).getOrCreate()


def get_gp_registration_output_records(
    gp_data: pyspark.sql.DataFrame,
    pds_data: pyspark.sql.DataFrame,
    sex_data: pyspark.sql.DataFrame,
    gp_practice: str = None,
):
    """Create a dataframe containing PDS record mismatch details.

    Args:
        gp_data (pyspark.sql.DataFrame): GDPPR dataframe.
        pds_data (pyspark.sql.DataFrame): PDS dataframe.
        sex_data (pyspark.sql.DataFrame): Sex codes lookup dataframe.
        gp_practice (str): Only process records from this GP practice.

    Returns:
        pyspark.sql.DataFrame
    """

    if gp_practice:
        gp_data = gp_data.where(col("practice") == gp_practice)

    gp_data.createOrReplaceTempView("gpddr")
    pds_data.createOrReplaceTempView("pds")
    sex_data.createOrReplaceTempView("sex_lkp")

    df = spark.sql(
        f"""
        SELECT GP.SURNAME,
               GP.FORENAME AS FORENAMES,
               date_format(to_date(cast(GP.DATE_OF_BIRTH as string),'yyyy-MM-dd'),'dd/MM/yyyy') `DOB`,
               GP.NHS_NUMBER AS `NHS NO.`,
               ADDRESS_1 as `ADD 1`,
               ADDRESS_2  as `ADD 2`,
               ADDRESS_3  as `ADD 3`,
               ADDRESS_4  as `ADD 4`,
               ADDRESS_5  as `ADD 5`,
               GP.POSTCODE,
               SLKP.sex AS SEX,
               CASE
                    WHEN (PDS.NHS_Number IS NULL) THEN 'Unmatched'
                    WHEN (GP.NHS_Number = PDS.NHS_Number AND GP.PRACTICE IS NOT NULL AND (PDS.gp.code IS NULL OR PDS.gp.code = "")) THEN 'Deducted Patient Match'
                    WHEN (GP.NHS_Number = PDS.NHS_Number AND (GP.PRACTICE <> PDS.gp.code AND (PDS.gp.code IS NOT NULL OR PDS.gp.code != ""))) THEN 'Partnership Mismatch'
                END AS STATUS,
                CASE
                    WHEN (PDS.NHS_Number IS NULL) THEN ''
                    WHEN (GP.NHS_Number = PDS.NHS_Number AND GP.PRACTICE <> PDS.gp.code) THEN date_format(to_date(cast(date 'today' as string),'yyyy-MM-dd'),'dd/MM/yyyy')
                    WHEN (GP.NHS_Number = PDS.NHS_Number AND PDS.gp.code IS NULL) THEN date_format(to_date(cast(date 'today' as string),'yyyy-MM-dd'),'dd/MM/yyyy')
                END AS `STATUS DATE`
        FROM gpddr GP
        LEFT JOIN pds PDS ON GP.NHS_Number = PDS.NHS_Number
        LEFT JOIN sex_lkp SLKP ON GP.SEX = SLKP.code
        WHERE (GP.NHS_Number IS NOT NULL AND PDS.NHS_Number IS NULL)
        OR (GP.NHS_Number=PDS.NHS_Number AND (GP.PRACTICE IS NOT NULL AND (PDS.gp.code IS NULL OR PDS.gp.code = "")))
        OR (GP.NHS_Number=PDS.NHS_Number AND GP.PRACTICE <> PDS.gp.code AND (PDS.gp.code IS NOT NULL OR PDS.gp.code != ""))
        """
    )

    return df


def output_gp_records_status(
    gp_records_status: pyspark.sql.DataFrame,
    pds_practice: str,
    bucket: str,
    out_path: Path,
    aws_access_key: str,
    aws_secret_key: str,
    on_databricks: bool = False,
):
    """Writes PDS registration differences csv files to an S3 bucket.

    Args:
        gp_records_status (pyspark.sql.DataFrame): GP registration differences DataFrame.
        pds_practice (str): GP Practice to filter.
        bucket (str): Bucket to save the file to.
        out_path (Path): Target output file in bucket.
        access_key (str): AWS public key.
        secret_key (str): AWS private key.
        on_databricks (bool): Set to True if this is running on databricks, to account for
            manipulation of file save locations.
    """
    filename = os.path.basename(out_path)
    df = gp_records_status.filter(col("PRACTICE") == pds_practice).drop(col("PRACTICE"))

    saved_file = save_to_csv(df, filename, on_databricks=on_databricks)

    upload_to_s3(saved_file, bucket, out_path, aws_access_key, aws_secret_key)


def gp_pds_comparison_with_unionable_result(
    gp_pds_df: pyspark.sql.DataFrame,
    gp_col: pyspark.sql.Column,
    pds_col: pyspark.sql.Column,
    og_gp_col: pyspark.sql.Column,
    og_pds_col: pyspark.sql.Column,
    item: str,
    action: str,
):
    """Creates a result dataframe containing rows filtered by simple equality
    comparison of gp_col with pds_col, literally `gp_col != pds_col`.

    Args:
        gp_pds_df (pyspark.sql.DataFrame): Dataframe containing GP and PDS
            records joined on NHS number
        gp_col (pyspark.sql.Column): Column from GP data, formatted for comparison if needed.
        pds_col (pyspark.sql.Column): Column from PDS data, formatted for comparison if needed.
        og_gp_col (pyspark.sql.Column): Original column from GP data.
        og_pds_col (pyspark.sql.Column): Original column from PDS data.
        item: Name of the item being compared.
        action: Action to take if the comparison is not equal.
    """
    return (
        gp_pds_df.filter(gp_col != pds_col)
        .withColumn(ACTION_COLUMN, lit(ACTION_REQUIRES_VALIDATION))
        .withColumn("item", lit(item))
        .select(
            "practice",
            "nhs_number",
            "item",
            og_gp_col.alias("gp_value"),
            og_pds_col.alias("pds_value"),
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
        pyspark.sql.DataFrame: Dataframe containing only records where the name
            is different, with a further action flag
    """

    udf_compare_patient_name = udf(compare_patient_name, ArrayType(StringType()))

    df = (
        gp_pds_df.where((gp_surname != pds_surname) | (gp_forenames != pds_forenames))
        .withColumn(
            "actions_items",
            udf_compare_patient_name(gp_forenames, gp_surname, pds_forenames, pds_surname),
        )
        .withColumn("actions", col("actions_items").getItem(0))
        .withColumn("items", col("actions_items").getItem(1))
    )

    both = df.where(col("items") == BOTH_NAMES)

    surname = (
        both.withColumn(ACTION_COLUMN, col("actions"))
        .withColumn("item", lit("surname"))
        .unionAll(
            df.where(col("items") == SURNAME)
            .withColumn(ACTION_COLUMN, col("actions"))
            .withColumn("item", lit("surname"))
        )
        .select(
            "practice",
            "nhs_number",
            "item",
            col("surname").alias("gp_value"),
            col("name.familyName").alias("pds_value"),
            ACTION_COLUMN,
        )
    )

    forename = (
        both.withColumn(ACTION_COLUMN, col("actions"))
        .withColumn("item", lit("forenames"))
        .unionAll(
            df.where(col("items") == FORENAME)
            .withColumn(ACTION_COLUMN, col("actions"))
            .withColumn("item", lit("forenames"))
        )
        .select(
            "practice",
            "nhs_number",
            "item",
            col("forename").alias("gp_value"),
            col("forenames").alias("pds_value"),
            ACTION_COLUMN,
        )
    )

    return surname.unionAll(forename)


def get_record_mismatch_summary(
    gp_df: pyspark.sql.DataFrame, pds_df: pyspark.sql.DataFrame, gp_practice: str = None
) -> pyspark.sql.DataFrame:
    """Create a dataframe containing summary of record mismatches between PDS and GDPPR.

    Args:
        gp_df (pyspark.sql.DataFrame): GP Practice dataframe.
        pds_df (pyspark.sql.DataFrame): PDS dataframe.
        gp_practice (str): Only process records from this GP practice.

    Returns:
        pyspark.sql.DataFrame
    """

    if gp_practice:
        pds_df = pds_df.where(col("gp.code") == gp_practice)
        gp_df = gp_df.where(col("practice") == gp_practice)

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
        JOIN pds_vw p ON g.practice = p.gp.code AND p.nhs_number = g.nhs_number
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
        INNER JOIN pds_vw p ON g.nhs_number = p.nhs_number AND g.practice = p.gp.code
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
    gp_df: pyspark.sql.DataFrame, pds_df: pyspark.sql.DataFrame, gp_practice: str = None
) -> pyspark.sql.DataFrame:
    """Generate a GP-PDS mismatches dataframe.

    Args:
        gp_df (pyspark.sql.DataFrame): GP Practice dataframe.
        pds_df (pyspark.sql.DataFrame): PDS dataframe.
        gp_practice (str): Only process records from this GP practice.

    Returns:
        pyspark.sql.DataFrame
    """

    if gp_practice:
        pds_df = pds_df.where(col("gp.code") == gp_practice)
        gp_df = gp_df.where(col("practice") == gp_practice)

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

    date_of_birth = gp_pds_comparison_with_unionable_result(
        gp_pds_df,
        col("date_of_birth"),
        to_date(col("pds_date_of_birth").cast("string"), "yyyyMMdd"),
        col("date_of_birth"),
        col("pds_date_of_birth"),
        "date_of_birth",
        ACTION_REQUIRES_VALIDATION,
    )
    date_of_birth.createOrReplaceTempView("vw_date_of_birth")

    name = compare_gp_pds_names(
        gp_pds_df,
        col("surname"),
        col("name.familyName"),
        col("forename"),
        col("forenames"),
    )
    name.createOrReplaceTempView("vw_name")

    sex = gp_pds_comparison_with_unionable_result(
        gp_pds_df,
        col("sex"),
        col("gender.gender"),
        col("sex"),
        col("gender.gender"),
        "sex",
        ACTION_REQUIRES_VALIDATION,
    )
    sex.createOrReplaceTempView("vw_sex")

    address = compare_gp_pds_address(gp_pds_df, col("gp_address"), col("address_lines"))
    address.createOrReplaceTempView("vw_address")

    postcode = compare_gp_pds_postcode(gp_pds_df, col("POSTCODE"), col("address.postcode"))
    postcode.createOrReplaceTempView("vw_postcode")

    gp_mismatched_data = spark.sql(
        """
        SELECT
            practice,
            nhs_number,
            item,
            gp_value,
            pds_value,
            action
        FROM vw_name
        UNION
        SELECT
            practice,
            nhs_number,
            item,
            gp_value,
            pds_value,
            action
        FROM vw_date_of_birth
        UNION
        SELECT
            practice,
            nhs_number,
            item,
            gp_value,
            pds_value,
            action
        FROM vw_sex
        UNION
        SELECT
            practice,
            nhs_number,
            'address' AS item,
            gp_value AS gp_value,
            pds_value AS pds_value,
            action as action
        FROM vw_address
        UNION
        SELECT
            practice,
            nhs_number,
            'postcode' AS item,
            gp_value AS gp_value,
            pds_value AS pds_value,
            action as action
        FROM vw_postcode
        """
    ).orderBy(["practice", "nhs_number"])

    return gp_mismatched_data


def get_pds_records_status(
    gp_df: pyspark.sql.DataFrame,
    pds_df: pyspark.sql.DataFrame,
    sex_lkp: pyspark.sql.DataFrame,
    gp_practice: str = None,
) -> pyspark.sql.DataFrame:
    """Create a dataframe containing PDS record mismatch details.

    Args:
        gp_df (pyspark.sql.DataFrame): GDPPR dataframe.
        pds_df (pyspark.sql.DataFrame): PDS dataframe.
        gp_practice (str): Only process records from this GP practice.
        sex_lkp (pyspark.sql.DataFrame): Sex lookup dataframe.

    Returns:
        pyspark.sql.DataFrame
    """

    if gp_practice:
        pds_df = pds_df.where(col("gp.code") == gp_practice)

    gp_df.createOrReplaceTempView("gp_vw")
    pds_df.createOrReplaceTempView("pds_vw")
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
    gp_records_status: pyspark.sql.DataFrame,
    gp_practice: str,
    bucket: str,
    directory: Path,
    aws_access_key: str,
    aws_secret_key: str,
    on_databricks: bool = False,
):
    """Writes registration differences csv files to an S3 bucket.

    Args:
        pds_records_status (pyspark.sql.DataFrame): PDS registration differences DataFrame.
        gp_records_status: (pyspark.sql.DataFrame): GP registration differences DataFrame.
        gp_practice (str): GP Practice to filter.
        bucket (str): Bucket to save the file to.
        directory (str): Target output directory in bucket. If targeting root, use ''
        aws_access_key (str): AWS public key.
        aws_secret_key (str): AWS private key.
        on_databricks (bool): Set to True if this is running on databricks, to account for
            manipulation of file save locations.
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
        on_databricks=on_databricks,
    )

    output_gp_records_status(
        gp_records_status,
        gp_practice,
        bucket,
        os.path.join(directory, gp_filename),
        aws_access_key,
        aws_secret_key,
        on_databricks=on_databricks,
    )


def output_demographic_mismatches(
    demographic_mismatches: pyspark.sql.DataFrame,
    gp_practice: str,
    bucket: str,
    directory: Path,
    aws_access_key: str,
    aws_secret_key: str,
    on_databricks: bool = False,
):
    """Writes demographic differences csv files to an S3 bucket.

    Args:
        demographic_mismatches (pyspark.sql.DataFrame): Demographic differences DataFrame.
        gp_practice (str): GP Practice to filter.
        bucket (str): Bucket to save the file to.
        directory (str): Target output directory in bucket. If targeting root, use ''
        aws_access_key (str): AWS public key.
        aws_secret_key (str): AWS private key.
        on_databricks (bool): Set to True if this is running on databricks, to account for
            manipulation of file save locations.
    """

    date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    mismatch_filename = f"{gp_practice}_Mismatch_{date}.csv"

    df = demographic_mismatches.filter(col("PRACTICE") == gp_practice).drop(col("PRACTICE"))
    saved_file = save_to_csv(df, mismatch_filename, on_databricks=on_databricks)

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
    on_databricks: bool = False,
):
    """Writes PDS registration differences csv files to an S3 bucket.

    Args:
        pds_records_status (pyspark.sql.DataFrame): PDS registration differences DataFrame.
        gp_practice (str): GP Practice to filter.
        bucket (str): Bucket to save the file to.
        out_path (Path): Target output file in bucket.
        aws_access_key (str): AWS public key.
        aws_secret_key (str): AWS private key.
        on_databricks (bool): Set to True if this is running on databricks, to account for
            manipulation of file save locations.
    """
    filename = os.path.basename(out_path)
    df = pds_records_status.filter(col("PRACTICE") == gp_practice).drop(col("PRACTICE"))
    saved_file = save_to_csv(df, filename, on_databricks=on_databricks)

    upload_to_s3(saved_file, bucket, out_path, aws_access_key, aws_secret_key)


def compare_gp_pds_address(
    gp_pds_df: pyspark.sql.DataFrame,
    gp_col: pyspark.sql.Column,
    pds_col: pyspark.sql.Column,
) -> pyspark.sql.DataFrame:
    """Check address differences between PDS and GP data and flag records
    for further action, creating a dataframe.

    Args:
        gp_pds_df (pyspark.sql.DataFrame): Dataframe containing GP and PDS
            records joined on NHS number
        gp_col (pyspark.sql.Column): Column from GP data for address.
        pds_col (pyspark.sql.Column): Column from PDS data for address.

    Returns:
        pyspark.sql.DataFrame: Dataframe containing only records where the address
            is different, with a further action flag
    """

    spaces_udf = udf(lambda x: update_spaces(x), StringType())
    caps_udf = udf(lambda x: update_caps(x), StringType())

    return (
        gp_pds_df.filter(caps_udf(spaces_udf(gp_col)) != caps_udf(spaces_udf(pds_col)))
        .withColumn(ACTION_COLUMN, lit(ACTION_REQUIRES_VALIDATION))
        .withColumn("item", lit("address"))
        .select(
            "practice",
            "nhs_number",
            "item",
            gp_col.alias("gp_value"),
            pds_col.alias("pds_value"),
            ACTION_COLUMN,
        )
    )


def compare_gp_pds_postcode(
    gp_pds_df: pyspark.sql.DataFrame,
    gp_col: pyspark.sql.Column,
    pds_col: pyspark.sql.Column,
) -> pyspark.sql.DataFrame:
    """Check postcode differences between PDS and GP data and flag records
    for further action, creating a dataframe.

    Args:
        gp_pds_df (pyspark.sql.DataFrame): Dataframe containing GP and PDS
            records joined on NHS number
        gp_col (pyspark.sql.Column): Column from GP data for postcode.
        pds_col (pyspark.sql.Column): Column from PDS data for postcode.

    Returns:
        pyspark.sql.DataFrame: Dataframe containing only records where the postcode
            is different, with a further action flag
    """
    spaces_udf = udf(lambda x: update_spaces(x), StringType())
    caps_udf = udf(lambda x: update_caps(x), StringType())

    return (
        gp_pds_df.filter(caps_udf(spaces_udf(gp_col)) != caps_udf(spaces_udf(pds_col)))
        .withColumn(ACTION_COLUMN, lit(ACTION_REQUIRES_VALIDATION))
        .withColumn("item", lit("postcode"))
        .select(
            "practice",
            "nhs_number",
            "item",
            gp_col.alias("gp_value"),
            pds_col.alias("pds_value"),
            ACTION_COLUMN,
        )
    )
