import csv
import os

import pandas
import pyspark

from listrec.databricks.matching import pds_gp_mismatches, get_pds_records_status
from listrec.databricks.utils import format_pds_mock_data

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")


def test_pds_gp_mismatches_records_correct():
    spark = pyspark.sql.SparkSession.builder.getOrCreate()

    with open(os.path.join(DATA, "gdppr.csv")) as infile:
        reader = csv.reader(infile)
        header = next(reader)
        rows = [r for r in reader]

    gp = spark.createDataFrame(
        rows,
        header,
    )

    gp.createOrReplaceTempView("vw_gdppr")

    with open(os.path.join(DATA, "pds.csv")) as infile:
        reader = csv.reader(infile)
        header = next(reader)
        rows = [r for r in reader]

    pds = spark.createDataFrame(
        rows,
        header,
    )

    pds = format_pds_mock_data(pds)
    pds.createOrReplaceTempView("vw_pds")

    expected = spark.createDataFrame(
        [
            (
                "Y06922",
                "8582405340",
                "date_of_birth",
                "2916-08-17",
                "19160817",
                "Further validation required",
            ),
            ("Y06922", "8582405340", "sex", "1", "9", None),
            (
                "Y06922",
                "8582405340",
                "postcode",
                "NotZE2 9AR",
                "ZE2 9AR",
                None,
            ),
            (
                "Y06922",
                "8582405340",
                "name",
                "Bondley, NotTerry",
                "Bondley, Terry",
                'Further validation required',
            ),
            (
                "Y06922",
                "8582405340",
                "address",
                "NotRedwing NotWolverhampton NotWinchester",
                "Redwing Wolverhampton Winchester",
                None
            ),
            (
                "Y06922",
                "8761038776",
                "name",
                "Kidwell, Lucais",
                "Lucais, Kidwell",
                'Update PDS name with GP name'
            ),
            (
                "Y06922",
                "2797516451",
                "name",
                "Rich Marvell, Kerwinn",
                "Marvell, Kerwinn",
                'Update PDS name with GP name'
            ),
            (
                "Y06922",
                "4698144396",
                "name",
                "Astridge, Nata Jones",
                "Astridge, Nata",
                'Update PDS name with GP name'
            ),
            (
                "Y06922",
                "0486072339",
                "name",
                ", Nelle",
                "Brumen, Nelle",
                'Update GP name with PDS name'),
            (
                "Y06922",
                "6414799785",
                "name",
                "De Mullett, Abe",
                "De Mullett, Abe-Rich",
                'Update GP name with PDS name'
            ),
            (
                "Y06922",
                "1304672999",
                "name",
                "Pavey, Nikki-Stevens",
                "Pavey, Nikki",
                'Update PDS name with GP name'
            ),
            (
                "Y06922",
                "4682621238",
                "name",
                "Das-Lee, Brianne",
                "Das Lee, Brianne",
                'Update PDS name with GP name'
            ),
            (
                "Y06922",
                "6472621238",
                "name",
                "Das, Brian Lee",
                "Das, Brian-Lee",
                'Update PDS name with GP name'
            ),

        ],
        ["practice", "nhs_number", "item", "gp_value", "pds_value", "action"],
    )

    actual = pds_gp_mismatches(gp, pds)

    pandas.testing.assert_frame_equal(
        actual.toPandas().sort_values(["nhs_number", "item"]).reset_index(drop=True),
        expected.toPandas().sort_values(["nhs_number", "item"]).reset_index(drop=True),
    )


def test_get_pds_exclusive_records_correct():
    spark = pyspark.sql.SparkSession.builder.config(
        "spark.driver.bindAddress", "127.0.0.1"
    ).getOrCreate()

    sex_lkp = spark.createDataFrame([[1, "M"], [2, "F"], [0, "I"], [9, "N"]], ["code", "sex"])

    gp = spark.createDataFrame(
        [
            ("123", "ABC"),
            ("789", "DEF"),
            ("012", None),
        ],
        ["NHS_Number", "practice"],
    )

    pds = spark.createDataFrame(
        [
            (
                "123",
                '{"familyName": "Jones", "givenNames": ["John"]}',
                "20010423",
                '{"lines": ["21 Hay Street", "Claydon", "Bury"], "postCode": "HP22 4QS"}',
                '{"gender": 1}',
                '{"code": "ABC", "from": 20040506}',
            ),
            (
                "456",
                '{"familyName": "Smith", "givenNames": ["Anne"]}',
                "19990423",
                '{"lines": ["31 Cray Street", "Haydon", "Tooting", "London", "London"], "postCode": "HP44 4QS"}',
                '{"gender": 2}',
                '{"code": "ABC", "from": 20040506}',
            ),
            (
                "789",
                '{"familyName": "Hogan", "givenNames": ["Joe", "Peter"]}',
                "19980423",
                '{"lines": ["45 Bay Street", "Haydon", "Barking", "London"], "postCode": "YO44 4QS"}',
                '{"gender": 1}',
                '{"code": "HIJ", "from": 20040506}',
            ),
            (
                "012",
                '{"familyName": "Bogan", "givenNames": ["Jan"]}',
                "19970423",
                '{"lines": ["43 Bay Street", "Haydon", "Barking", "London"], "postCode": "YO44 4QS"}',
                '{"gender": 0}',
                '{"code": "KLM", "from": 20040506}',
            ),
        ],
        ["NHS_Number", "name", "date_of_birth", "address", "gender", "gp"],
    )
    pds = format_pds_mock_data(pds)

    expected = spark.createDataFrame(
        [
            (
                "Bogan",
                "Jan",
                "23/04/1997",
                "012",
                "KLM",
                "43 Bay Street",
                "Haydon",
                "Barking",
                "London",
                None,
                "YO44 4QS",
                "I",
                "06/05/2004",
            ),
            (
                "Smith",
                "Anne",
                "23/04/1999",
                "456",
                "ABC",
                "31 Cray Street",
                "Haydon",
                "Tooting",
                "London",
                "London",
                "HP44 4QS",
                "F",
                "06/05/2004",
            ),
            (
                "Hogan",
                "Joe Peter",
                "23/04/1998",
                "789",
                "HIJ",
                "45 Bay Street",
                "Haydon",
                "Barking",
                "London",
                None,
                "YO44 4QS",
                "M",
                "06/05/2004",
            ),
        ],
        [
            "SURNAME",
            "FORENAMES",
            "DOB",
            "NHS NO.",
            "PRACTICE",
            "ADD 1",
            "ADD 2",
            "ADD 3",
            "ADD 4",
            "ADD 5",
            "POSTCODE",
            "SEX",
            "DATE_ACCEPT.",
        ],
    )
    actual = get_pds_records_status(gp, pds, sex_lkp)

    pandas.testing.assert_frame_equal(
        actual.toPandas().sort_values("NHS NO.").reset_index(drop=True),
        expected.toPandas().sort_values("NHS NO.").reset_index(drop=True),
    )
