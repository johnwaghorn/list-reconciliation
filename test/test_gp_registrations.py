import pandas
import pyspark
from datetime import datetime
from pathlib import Path

from listrec.databricks.matching import get_gp_registration_output_records
from listrec.databricks.utils import format_pds_data


def test_get_gp_registration_output_records():

    spark = pyspark.sql.SparkSession.builder.config(
        "spark.driver.bindAddress", "127.0.0.1"
    ).getOrCreate()

    sex_lkp = spark.createDataFrame(
        [["1", "M"], ["2", "F"], ["0", "I"], ["9", "N"]], ["code", "sex"]
    )

    gp = spark.createDataFrame(
        [
            (
                "Boris",
                "Becker",
                "2012-05-23",
                "6937065701",
                "43 Bay Street",
                "Haydon",
                "Barking",
                "London",
                None,
                "TW12 4DP",
                "0",
                "Deducted Patient Match",
                "04/04/2021",
                "P123",
            ),
            (
                "Pete",
                "Sampras",
                "2011-10-11",
                "2316305156",
                "31 Cray Street",
                "Haydon",
                "Tooting",
                None,
                "London",
                "SN1 3SE",
                "1",
                "Deducted Patient Match",
                "04/04/2021",
                "P731",
            ),
            (
                "Andre",
                "Agassi",
                "2016-08-17",
                "4644873489",
                "45 Bay Street",
                "Haydon",
                "Barking",
                "London",
                "London",
                "WS1 3ED",
                "2",
                "Unmatched",
                "",
                "P849",
            ),
            (
                "Steffi",
                "Graf",
                "2013-08-17",
                "2316305155",
                "23 Corn Street",
                "Riding",
                "Reading",
                "",
                "London",
                "PE1 3WS",
                "2",
                "Partnership Mismatch",
                "04/04/2021",
                "P849",
            ),
            (
                "X",
                "Y",
                "2013-08-17",
                "2316305150",
                "23 Corn Street",
                "Riding",
                "Reading",
                "",
                "London",
                "PE1 3WS",
                "9",
                "Partnership Mismatch",
                "04/04/2021",
                "P849",
            ),
        ],
        [
            "SURNAME",
            "FORENAME",
            "DATE_OF_BIRTH",
            "NHS_Number",
            "ADDRESS_1",
            "ADDRESS_2",
            "ADDRESS_3",
            "ADDRESS_4",
            "ADDRESS_5",
            "POSTCODE",
            "SEX",
            "STATUS",
            "STATUS DATE",
            "PRACTICE",
        ],
    )

    pds = spark.createDataFrame(
        [
            ("6937065701", '{"code": "P123", "from": 20040506}'),
            ("2316305156", '{"code": "", "from": 20040506}'),
            ("2316305155", '{"code": "P980", "from": 20040506}'),
            ("2316305150", '{"code": "P850", "from": 20040506}'),
        ],
        ["NHS_Number", "gp"],
    )

    pds = format_pds_data(pds)

    actual = get_gp_registration_output_records(gp, pds, sex_lkp)

    expected = spark.createDataFrame(
        [
            (
                "Pete",
                "Sampras",
                "11/10/2011",
                "2316305156",
                "31 Cray Street",
                "Haydon",
                "Tooting",
                None,
                "London",
                "SN1 3SE",
                "M",
                "Deducted Patient Match",
                datetime.now().strftime("%d/%m/%Y"),
            ),
            (
                "Andre",
                "Agassi",
                "17/08/2016",
                "4644873489",
                "45 Bay Street",
                "Haydon",
                "Barking",
                "London",
                "London",
                "WS1 3ED",
                "F",
                "Unmatched",
                "",
            ),
            (
                "Steffi",
                "Graf",
                "17/08/2013",
                "2316305155",
                "23 Corn Street",
                "Riding",
                "Reading",
                "",
                "London",
                "PE1 3WS",
                "F",
                "Partnership Mismatch",
                datetime.now().strftime("%d/%m/%Y"),
            ),
            (
                "X",
                "Y",
                "17/08/2013",
                "2316305150",
                "23 Corn Street",
                "Riding",
                "Reading",
                "",
                "London",
                "PE1 3WS",
                "N",
                "Partnership Mismatch",
                datetime.now().strftime("%d/%m/%Y"),
            ),
        ],
        [
            "SURNAME",
            "FORENAMES",
            "DOB",
            "NHS NO.",
            "ADD 1",
            "ADD 2",
            "ADD 3",
            "ADD 4",
            "ADD 5",
            "POSTCODE",
            "SEX",
            "STATUS",
            "STATUS DATE",
        ],
    )

    pandas.testing.assert_frame_equal(
        actual.toPandas().sort_values("NHS NO.").reset_index(drop=True),
        expected.toPandas().sort_values("NHS NO.").reset_index(drop=True),
    )
