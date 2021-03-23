import tempfile
import os

import pyspark

from listrec.utils import save_to_csv


def test_save_to_csv_saves_correctly():
    spark = pyspark.sql.SparkSession.builder.appName("testspark").getOrCreate()
    dataframe = spark.createDataFrame([(1, 2, 3, 4)], ["h1", "h2", "h3", "h4"])

    out_file = save_to_csv(
        dataframe, os.path.join(tempfile.tempdir, "out.csv"), on_databricks=False
    )
    actual = open(out_file).readlines()
    expected = ["h1,h2,h3,h4\n", "1,2,3,4\n"]

    assert actual == expected
