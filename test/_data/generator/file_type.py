import csv
import gzip
import os
import shutil

from abc import ABC, abstractmethod

import dps_pds
import gp
import pds

# TODO ensure exists, put somewhere better
TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp")


class FileType(ABC):
    """Abstract File Type Class"""

    @abstractmethod
    def _create_row():
        """create a row"""

    @abstractmethod
    def create_file():
        """create a file"""


class PDSData(FileType):
    def _create_row(self):
        return pds.create_patient()

    def create_file(self, row_count):
        filename = pds.create_filename(row_count)
        file = os.path.join(TEMP_DIR, filename)

        # create csv of given size
        with open(file, "w", newline="") as csvfile:
            data = csv.writer(csvfile)
            data.writerow(self._create_row().keys())

            for _ in range(row_count):
                data.writerow(self._create_row().values())

        # return filepath of gzipped file
        return file


class DPSPDSData(FileType):
    def _create_row(self):
        return dps_pds.create_patient()

    # TODO create in temp location, then use Storage Class to Store
    def create_file(self, row_count):
        filename = dps_pds.create_filename(row_count)
        file = os.path.join(TEMP_DIR, filename)
        output = f"{file}.gz"

        # create csv of given size
        with open(file, "w", newline="") as csvfile:
            data = csv.writer(csvfile)
            data.writerow(["nhs_number", "gp_practice", "dispensing_flag"])

            for _ in range(row_count):
                data.writerow(self._create_row())

        # compress with gzip
        with open(file, "rb") as csvfile:
            with gzip.open(output, "wb") as f_out:
                shutil.copyfileobj(csvfile, f_out)

        # delete uncompressed file
        os.remove(file)

        # return filepath of gzipped file
        return output


class GPData(FileType):
    def _create_row(self):
        pass

    def create_file(self, row_count):
        gp_code = "GPCODE"  # TODO [A-Z][0-9]{5}
        ha_cipher = "LNA"  # TODO [A-Z0-9]{3}
        valid_date = gp.generate_valid_date()
        file_letter = "A"  # this is the multi-file identifier, which is not currently supported in List Rec

        filename = gp.create_filename(gp_code, ha_cipher, valid_date, file_letter)
        file = os.path.join(TEMP_DIR, filename)

        # create csv of given size
        with open(file, "w", newline="") as csvfile:
            data = csv.writer(csvfile, delimiter="~", quoting=csv.QUOTE_NONE)
            # Write "header" row
            data.writerow([r"503\*"])
            for _ in range(row_count):
                # TODO use create row?
                data.writerow(gp.first_part())
                data.writerow(gp.second_part())

        return file
