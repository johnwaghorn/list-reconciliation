import pandas
import pyspark

from listrec.databricks.matching import get_pds_records_status
from listrec.databricks.utils import format_pds_mock_data


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
