import csv
import gzip
import os
import shutil
import sys

from faker import Faker
from faker.providers import BaseProvider

from .dps_pds_ref_data import gp_practices


class NHSNumber(BaseProvider):
    def nhs_number(self):
        return self.random_number(digits=10, fix_len=True)


class GPPractice(BaseProvider):
    def gp_practice(self):
        return self.random_element(gp_practices)


class DispensingFlag(BaseProvider):
    def dispensing_flag(self):
        return self.random_element([0, 1])


fake = Faker()
fake.add_provider(NHSNumber)
fake.add_provider(GPPractice)
fake.add_provider(DispensingFlag)


def generate(size) -> str:
    file = f"{os.path.dirname(os.path.abspath(__file__))}/dps_pds_data_{size}.csv"
    output = f"{file}.gz"

    # create csv of given size
    with open(file, "w", newline="") as csvfile:
        dps_pds_data = csv.writer(csvfile)
        dps_pds_data.writerow(["nhs_number", "gp_practice", "dispensing_flag"])

        for _ in range(size):
            dps_pds_data.writerow([fake.nhs_number(), fake.gp_practice(), fake.dispensing_flag()])

    # compress with gzip
    with open(file, "rb") as csvfile:
        with gzip.open(output, "wb") as f_out:
            shutil.copyfileobj(csvfile, f_out)

    # delete uncompressed file
    os.remove(file)

    # return filepath of gzipped file
    return output


if __name__ == "__main__":
    size = int(sys.argv[1]) if len(sys.argv) == 2 else 67
    generate(size)
