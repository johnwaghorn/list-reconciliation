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
                record = dps_pds.Record().get()
                data.writerow(record)

        # compress with gzip
        with open(file, "rb") as csvfile:
            with gzip.open(output, "wb") as f_out:
                shutil.copyfileobj(csvfile, f_out)

        # delete uncompressed file
        os.remove(file)

        # return filepath of gzipped file
        return output

    def split_from_pds(
        self,
        pds_filename,
        not_on_pds_differences_count=0,
        demographic_differences_count=0,
    ):
        filename = dps_pds.create_filename("from_pds_data")
        file = os.path.join(TEMP_DIR, filename)

        pds_file = open(pds_filename)
        pds_dps_file = open(file, "w")

        data = csv.writer(pds_dps_file)
        # TODO get headers from Record
        data.writerow(["nhs_number", "gp_practice", "dispensing_flag"])

        pds_file_reader = csv.reader(pds_file)

        for patient in pds_file_reader:
            if patient[0] == "NHS_NUMBER":
                continue

            record = dps_pds.Record(
                nhs_number=patient[0],
                gp_practice=patient[15],
                dispensing_flag=patient[18],
            ).get()
            data.writerow(record)

        pds_file.close()

        # create X number of new rows, via the PDS Generator, to create notInPDS differences
        self._create_not_on_pds_differences(pds_dps_file, not_on_pds_differences_count)
        # mutate X number of rows, changing dispensing_flag, to create demographic differences
        self._create_demographic_differences(
            pds_dps_file, demographic_differences_count
        )

        pds_dps_file.close()

        # compress with gzip
        output = f"{file}.gz"
        with open(file, "rb") as csvfile:
            with gzip.open(output, "wb") as f_out:
                shutil.copyfileobj(csvfile, f_out)

        # delete uncompressed file
        os.remove(file)

        # return filepath of gzipped file
        print(f"created file {output}")
        return output

    def _create_not_on_pds_differences(self, file, count):
        print(f"Creating {count} Not on PDS Differences in {file.name}")

    def _create_demographic_differences(self, file, count):
        print(f"Creating {count} Demographic Differences in {file.name}")


class GPData(FileType):
    def _create_row(self):
        pass

    def create_file(self, row_count):
        gp_practice_code = "GPCODE"  # TODO [A-Z][0-9]{5}
        ha_cipher = "LNA"  # TODO [A-Z0-9]{3}
        valid_date = gp.generate_valid_date()
        file_letter = "A"  # this is the multi-file identifier, which is not currently supported in List Rec

        filename = gp.create_filename(
            gp_practice_code, ha_cipher, valid_date, file_letter
        )
        file = os.path.join(TEMP_DIR, filename)

        # create csv of given size
        with open(file, "w", newline="") as csvfile:
            data = csv.writer(csvfile, delimiter="~", quoting=csv.QUOTE_NONE)
            # Write "header" row
            data.writerow([r"503\*"])
            for _ in range(row_count):
                record = gp.Record().get()
                data.writerow(record[:16])
                data.writerow(record[16:])

        return file

    def split_from_pds(
        self,
        pds_filename,
        gp_practice_code,
        not_on_gp_differences_count=0,
        not_on_pds_differences_count=0,
        demographic_differences_count=0,
    ):
        ha_cipher = "LNA"  # TODO [A-Z0-9]{3}
        valid_date = gp.generate_valid_date()
        file_letter = "A"  # this is the multi-file identifier, which is not currently supported in List Rec

        filename = gp.create_filename(
            gp_practice_code, ha_cipher, valid_date, file_letter
        )
        file = os.path.join(TEMP_DIR, filename)

        pds_file = open(pds_filename)
        gp_file = open(file, "w")

        data = csv.writer(gp_file, delimiter="~", quoting=csv.QUOTE_NONE)
        data.writerow([r"503\*"])

        pds_file_reader = csv.reader(pds_file)

        for patient in pds_file_reader:
            if patient[15] != gp_practice_code:
                continue

            record = gp.Record(
                ha_cipher=ha_cipher,
                nhs_number=patient[0],
                family_name=patient[3],
                given_name=patient[4],
                other_given_name=patient[5],
                title=patient[6],
                gender=patient[7],
                date_of_birth=patient[1],
                address_line_1=patient[8],
                address_line_2=patient[9],
                address_line_3=patient[10],
                address_line_4=patient[11],
                address_line_5=patient[12],
                post_code=patient[17],
                drugs_dispensed_marker=patient[18],
            ).get()
            data.writerow(record[:16])
            data.writerow(record[16:])

        pds_file.close()

        # remove X number of rows from gp_file to create notInGP differences
        self._create_not_on_gp_differences(gp_file, not_on_gp_differences_count)
        # create X number of new rows, via the PDS Generator, to create notInPDS differences
        self._create_not_on_pds_differences(gp_file, not_on_pds_differences_count)
        # mutate X number of rows, changing names/addresses/gender etc, to create demographic differences
        self._create_demographic_differences(gp_file, demographic_differences_count)

        gp_file.close()

        print(f"created file {file}")

        return file

    def _create_not_on_gp_differences(self, file, count):
        print(f"Creating {count} Not on GP Differences in {file.name}")

    def _create_not_on_pds_differences(self, file, count):
        print(f"Creating {count} Not on PDS Differences in {file.name}")

    def _create_demographic_differences(self, file, count):
        print(f"Creating {count} Demographic Differences in {file.name}")
