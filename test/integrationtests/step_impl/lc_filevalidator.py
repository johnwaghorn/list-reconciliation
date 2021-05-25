import os
import shutil
import subprocess
import csv

from tempfile import gettempdir

from getgauge.python import step

TEMP_DIR = gettempdir()
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
    
@step(
    "run gpextract for scenario <Description> using file <File> and date <DateTime> and ensure expected message is <Expected Message>"
)
def run_gpextract(description, file1, freezedatetime, expmessage):
    # Print the description
    print (description)

    # Initial Filenames
    initial_file_name1 = os.path.join(DATA, "GPR4LNA1.A1A")

    temp_dir = gettempdir()

    # Destination Filenames
    destination_file_name1 = os.path.join(temp_dir, file1)

    # Copy test files to new filenames
    shutil.copy(initial_file_name1, destination_file_name1)

    # output path
    out_path = gettempdir()

    # Define the command to execute
    cmd = f"gpextract {out_path} {destination_file_name1} -t 0 -r --process_date {freezedatetime}".split()

    # Execute the command
    output = subprocess.check_output(cmd).decode()

    output = output.replace("\r", "").replace("\n", "").strip()

    assert (
        output == expmessage
    ), f"Expected is: \n\t{expmessage}\nbut invalid message thrown was: \n\t{output}"

@step(
    "assert <records> file keys are as expected"
)
def assert_record_file_keys(file):
    filename = os.path.join(TEMP_DIR, file)
    f = open(filename)
    data = csv.reader(f, delimiter=',')
    list_of_column_names = []
    for row in data:
            list_of_column_names.append(row)
            break
    
    actual_keys = list_of_column_names[0]
    expected_keys = ['_INVALID_', 'RECORD_TYPE', 'REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE', 'TRADING_PARTNER_NHAIS_CIPHER', 'DATE_OF_DOWNLOAD', 'TRANS_ID', 'NHS_NUMBER', 'SURNAME', 'FORENAMES', 'PREV_SURNAME', 'TITLE', 'SEX', 'DOB', 'ADDRESS_LINE1', 'ADDRESS_LINE2', 'ADDRESS_LINE3', 'ADDRESS_LINE4', 'ADDRESS_LINE5', 'POSTCODE', 'DRUGS_DISPENSED_MARKER', 'RPP_MILEAGE', 'BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER', 'WALKING_UNITS', 'RESIDENTIAL_INSTITUTE_CODE']
    assert expected_keys == actual_keys

@step(
    "run gpextract for scenario using not existing file and ensure expected message is <Expected Message>"
    )
def run_gpextract_file_not_found(expmessage):
    file1 = 'GPR4LNA1.EDA'
    
    # output path
    out_path = gettempdir()

    # Define the command to execute
    cmd = f"gpextract {out_path} {file1} -t 0 -r".split()
    
    # Execute the command
    output = subprocess.check_output(cmd).decode()

    output = output.replace("\r", "").replace("\n", "").strip()
    assert (
        output == expmessage
        ), f"Expected is: \n\t{expmessage}\nbut invalid message thrown was: \n\t{output}"