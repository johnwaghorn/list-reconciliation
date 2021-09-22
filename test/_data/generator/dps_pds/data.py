import csv
import gzip
import os
import shutil

from dps_pds.record import Record
from generator.storage.locations import TEMP_DIR


class DPSPDSData:
    @staticmethod
    def create_filename(name):
        return f"dps_pds_data_{name}.csv"

    # TODO create in temp location, then use Storage Class to Store
    def create_file(self, row_count):
        filename = self.create_filename(row_count)
        file = os.path.join(TEMP_DIR, filename)
        output = f"{file}.gz"

        # create csv of given size
        with open(file, "w", newline="") as csvfile:
            data = csv.writer(csvfile)
            data.writerow(["nhs_number", "gp_practice", "dispensing_flag"])

            for _ in range(row_count):
                record = Record().get()
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
        filename = self.create_filename("from_pds_data")
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

            record = Record(
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
