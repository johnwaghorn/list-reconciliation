import os
import urllib.parse
import urllib.request
import requests
import json
from tempfile import gettempdir

from getgauge.python import step

TEMP_DIR = gettempdir()
URL = "https://api.mockaroo.com/api/a544c330"


@step("check and remove if file <file> exists")
def before_hooks_removefile(file):

    destfile = os.path.join(TEMP_DIR, file)
    if os.path.exists(destfile):
        os.remove(destfile)


@step("run the mock api to generate <count> mock gprecords for key <key>")
def run_mock_api(count, key):

    # build the apil url and run
    params = [("count", count), ("key", key)]
    pairs = urllib.parse.urlencode(params)
    url = URL + "?" + pairs

    response = requests.get(url)

    with open(os.path.join(TEMP_DIR, "gpdata.json"), "w", newline="\n", encoding="utf-8") as f:
        f.writelines(response.text)
        f.close()


@step("assert if the <file> file keys exists")
def validate_file_keysExist(file):
    filename = os.path.join(TEMP_DIR, file)
    f = open(filename)
    data = json.load(f)
    for row in data:
        expected_keys = sorted(
            [
                "ADDRESS",
                "ADDRESS_1",
                "ADDRESS_2",
                "ADDRESS_3",
                "ADDRESS_4",
                "ADDRESS_5",
                "CODE",
                "DATE",
                "DATE_OF_BIRTH",
                "DATE_OF_DEATH",
                "EPISODE_CONDITION",
                "EPISODE_PRESCRIPTION",
                "ETHNIC",
                "FORENAME",
                "GP_SYSTEM_SUPPLIER",
                "JOURNAL_REPORTING_PERIOD_END_DATE",
                "LINKS",
                "LSOA",
                "NHS_NUMBER",
                "PDS_ACTIVITY_DATE",
                "PDS_DATE_OF_BIRTH",
                "PDS_DATE_OF_DEATH",
                "PDS_MONTH_OF_BIRTH",
                "PDS_NHS_NUMBER",
                "PDS_SERIAL_CHANGE_NUMBER",
                "PDS_YEAR_OF_BIRTH",
                "PDS_address",
                "PDS_emailAddress",
                "PDS_gender",
                "PDS_gp",
                "PDS_mobilePhone",
                "PDS_name",
                "PDS_sensitive",
                "PDS_telephone",
                "POSTCODE",
                "PRACTICE",
                "PROCESSED_TIMESTAMP",
                "RECORD_DATE",
                "REPORTING_PERIOD_END_DATE",
                "SENSITIVE_CODE",
                "SEX",
                "SURNAME",
                "VALUE1_CONDITION",
                "VALUE1_PRESCRIPTION",
                "VALUE2_CONDITION",
                "VALUE2_PRESCRIPTION",
                "YEAR_OF_BIRTH",
                "YEAR_OF_DEATH",
            ]
        )
        actual_keys = sorted(list(row.keys()))
        assert expected_keys == actual_keys


@step("assert the number of rows created is <number> in file <file>")
def number_of_records(number, file):
    filename = os.path.join(TEMP_DIR, file)
    f = open(filename)
    data = json.load(f)
    num = len(data)
    assert num == int(number), "The records count is invalid"
