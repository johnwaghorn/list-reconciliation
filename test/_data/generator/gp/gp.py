import random
from datetime import datetime, timedelta

from faker import Faker
from faker.providers import BaseProvider


class TransactionId(BaseProvider):
    def transaction_id(self):
        return self.random_number(digits=6, fix_len=True)


class PatientGender(BaseProvider):
    def patient_gender(self):
        return self.random_element([1, 2, 3, 3, 9])
        # return self.random_element({"Male": 1, "Female": 2, "Not known": 3, "Indeterminate": 3, "Not Specified": 9})


def generate_valid_date():
    random_day = random.randint(1, 14)
    now = datetime.now()
    days_ago = now - timedelta(days=random_day)
    return days_ago


def create_filename(gp_code, ha_cipher, valid_date, file_letter):
    months = "ABCDEFGHIJKL"
    days = "123456789ABCDEFGHIJKLMNOPQRSTUV"
    return f"{gp_code}_GPR4{ha_cipher}1.{months[valid_date.month-1]}{days[valid_date.day-1]}{file_letter}"


fake = Faker()
fake.add_provider(TransactionId)
fake.add_provider(PatientGender)

# TODO can we validate this test data against packages/gp_file_parser?


def first_part():
    return [
        "DOW",  # Static record identifier
        "1",  # Static record part identifier
        "1111111,1234",  # TODO GP Codes
        "LNA",  # TODO this must match the HA Cipher in the filename
        "20210623",  # TODO Date, must be less than 14 days old
        "1500",  # TODO Time
        str(fake.transaction_id()),  # Random positive integer
        "NHS_NUMBER",  # TODO
        "FAMILY_NAME",  # TODO
        "GIVEN_NAME",  # TODO
        "OTHER_GIVEN_NAME",  # TODO
        "TITLE",  # TODO
        str(fake.patient_gender()),
        "DATE_OF_BIRTH",  # TODO
        "ADDRESS_LINE_1",  # TODO
        "ADDRESS_LINE_2",  # TODO
    ]


def second_part():
    return [
        "DOW",
        "2",
        "ADDRESS_LINE_3",  # TODO
        "ADDRESS_LINE_4",  # TODO
        "ADDRESS_LINE_5",  # TODO
        "POST_CODE",  # TODO
        "",
        "3",  # TODO
        "",
        "",
        "",
    ]
