import csv
import os

from generator.storage.locations import TEMP_DIR
from pds.faker import create_patient


class PDSData:
    @staticmethod
    def create_filename(row_count):
        return f"pds_data_{row_count}.csv"

    def create_file(self, row_count):
        filename = self.create_filename(row_count)
        file = os.path.join(TEMP_DIR, filename)

        # create csv of given size
        with open(file, "w", newline="") as csvfile:
            data = csv.writer(csvfile)
            data.writerow(create_patient().keys())

            for _ in range(row_count):
                data.writerow(create_patient().values())

        # return filepath of gzipped file
        return file
