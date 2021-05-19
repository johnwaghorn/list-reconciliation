import os
import shutil
import subprocess

from tempfile import gettempdir

from getgauge.python import step


ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")


@step(
    "run gpextract for <file1> and date <datetime> and expected message is <expmessage>"
)
def run_gpextract(file1, freezedatetime, expmessage):

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
