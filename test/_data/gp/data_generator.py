import string

from config import config
import csv
from datetime import datetime, timedelta
import random
import argparse

PATIENT_GENDER = {"Male": 1, "Female": 2, "Not known": 3, "Indeterminate": 3, "Not Specified": 9}
MONTHS = "ABCDEFGHIJKL"
DAYS = "123456789ABCDEFGHIJKLMNOPQRSTUV"


class DataGenerator:
    def __init__(self, env, scenario=None):
        self.env_name = env
        self.test_scenario = scenario
        try:
            self.env = config[self.env_name]
        except KeyError:
            print(f"{env} is not valid environment \nValid environments are {list(config.keys())}")
            exit()
        self.gp_code = self.env["gp_code"]
        self.gp_file_name = self.env["gp_code"]
        if not self.test_scenario:
            self.pds_data_file = self.env["scenario"]["happy_path"]
        else:
            self.pds_data_file = self.env["scenario"][self.test_scenario]
        with open(self.pds_data_file) as pds_data:
            csv_reader = csv.DictReader(pds_data, delimiter=",")
            self.data = sorted(
                csv_reader, key=lambda row: row["PRIMARY_CARE_CODE"] == self.gp_code, reverse=True
            )

    def get_random_record_details(self):
        pass

    def generate_files(self):
        file_name = self.construct_gp_filename()
        print(
            f"Generating GP file '{self.env_name}' , File name:{file_name}  with GP Code: {self.gp_code}"
        )

        with open(file_name, "w") as f:
            header = "503\*\n"
            f.write(header)
            for row in self.data:
                record_1 = f"DOW~1~1111111,1234~LNA~20210623~1500~{self.transaction_id()}~{row['NHS_NUMBER']}~{row['FAMILY_NAME']}~{row['GIVEN_NAME']}~{row['OTHER_GIVEN_NAME']}~{row['TITLE']}~{PATIENT_GENDER[row['GENDER']]}~{row['DATE_OF_BIRTH']}~{row['ADDRESS_LINE_1']}~{row['ADDRESS_LINE_2']} "
                record_2 = f"DOW~2~{row['ADDRESS_LINE_3']}~{row['ADDRESS_LINE_4']}~{row['ADDRESS_LINE_5']}~{row['POST_CODE']}~~3~~~"
                f.write(f"{record_1}\n")
                f.write(f"{record_2}\n")

    @staticmethod
    def transaction_id():
        return random.randint(100000, 999999)

    @staticmethod
    def generate_valid_date():
        random_day = random.randint(1, 14)
        now = datetime.now()
        days_ago = now - timedelta(days=random_day)
        return days_ago

    def construct_gp_filename(self):
        valid_date = self.generate_valid_date()
        file_letter = random.choice(string.ascii_uppercase)
        return (
            f"{self.gp_code}_GPR4LNA1.{MONTHS[valid_date.month]}{DAYS[valid_date.day]}{file_letter}"
        )

    def main(self):
        self.generate_files()


if __name__ == "__main__":
    # run this script as python data_generator.py --env ref
    # optionally can pass --scenario arg as well (TBD)
    # env and scenario are defined in config file
    parser = argparse.ArgumentParser(description="List Rec Data generator")
    parser.add_argument("--env", type=str)
    parser.add_argument("--scenario", type=str)
    args = parser.parse_args()
    gen = DataGenerator(args.env)
    gen.main()
