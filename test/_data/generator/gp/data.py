import csv
import os
import random
from datetime import datetime, timedelta

from generator.storage.locations import TEMP_DIR
from gp.record import Record


class GPData:
    @staticmethod
    def create_filename(gp_code, ha_cipher, valid_date, file_letter):
        months = "ABCDEFGHIJKL"
        days = "123456789ABCDEFGHIJKLMNOPQRSTUV"
        return f"{gp_code}_GPR4{ha_cipher}1.{months[valid_date.month-1]}{days[valid_date.day-1]}{file_letter}"

    def create_file(self, row_count):
        gp_practice_code = "GPCODE"  # TODO [A-Z][0-9]{5}
        ha_cipher = "LNA"  # TODO [A-Z0-9]{3}
        valid_date = self.generate_valid_date()
        file_letter = "A"  # this is the multi-file identifier, which is not currently supported in List Rec

        filename = self.create_filename(
            gp_practice_code, ha_cipher, valid_date, file_letter
        )
        file = os.path.join(TEMP_DIR, filename)

        # create csv of given size
        with open(file, "w", newline="") as csvfile:
            data = csv.writer(csvfile, delimiter="~", quoting=csv.QUOTE_NONE)
            # Write "header" row
            data.writerow([r"503\*"])
            for _ in range(row_count):
                record = Record().get()
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
        valid_date = self.generate_valid_date()
        file_letter = "A"  # this is the multi-file identifier, which is not currently supported in List Rec

        filename = self.create_filename(
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

            record = Record(
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

    @staticmethod
    def generate_valid_date():
        random_day = random.randint(1, 14)
        now = datetime.now()
        days_ago = now - timedelta(days=random_day)
        return days_ago
