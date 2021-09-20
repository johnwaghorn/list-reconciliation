import os

from file_type import GPData
from storage import LocalStorage


class Splitter:
    def main(self):
        gp_practice_code = "K82070"
        pds_filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "pds_data_1000000.csv"
        )

        file = GPData()
        storage = LocalStorage()

        storage.store(file.split_from_pds(pds_filename, gp_practice_code))


if __name__ == "__main__":
    split = Splitter()
    split.main()
