import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from faker import Faker
from faker.providers import BaseProvider

GENDER = {
    "Male": "1",
    "Female": "2",
    "Not known": "3",
    "Indeterminate": "3",
    "Not Specified": "9",
}

DRUGS_DISPENSED_MARKER = {"1": "Y", "0": "N"}


class GP(BaseProvider):
    def transaction_id(self):
        return str(self.random_number(digits=6, fix_len=True))

    def patient_gender(self):
        return str(self.random_element([1, 2, 3, 3, 9]))
        # return self.random_element({"Male": 1, "Female": 2, "Not known": 3, "Indeterminate": 3, "Not Specified": 9})


fake = Faker()
fake.add_provider(GP)


@dataclass
class RecordPartOne:
    record_identifier: str = "DOW"
    record_part: str = "1"
    gp_practice_codes: str = "1111111,1234"
    ha_cipher: str = "LNA"
    export_date: str = "20210919"  # TODO always be yesterday?
    export_time: str = "1500"
    transaction_id: str = ""
    nhs_number: str = ""
    family_name: str = ""
    given_name: str = ""
    other_given_name: str = ""
    title: str = ""
    gender: str = fake.patient_gender()
    date_of_birth: str = ""
    address_line_1: str = ""
    address_line_2: str = ""

    def get_formatted_record(self) -> list[str]:
        return [
            self.record_identifier,
            self.record_part,
            self.gp_practice_codes,
            self.ha_cipher,
            self.export_date,
            self.export_time,
            self.transaction_id,
            self.nhs_number,
            self.family_name,
            self.given_name,
            self.other_given_name,
            self.title,
            GENDER[self.gender],
            self.date_of_birth,
            self.address_line_1,
            self.address_line_2,
        ]


@dataclass
class RecordPartTwo:
    record_identifier: str = "DOW"
    record_part: str = "2"
    address_line_3: str = ""
    address_line_4: str = ""
    address_line_5: str = ""
    post_code: str = ""
    drugs_dispensed_marker: str = ""
    rpp_mileage: str = ""
    special_district_marker: str = ""
    walking_units: str = ""
    residential_institute_code: str = ""

    def get_formatted_record(self) -> list[str]:
        return [
            self.record_identifier,
            self.record_part,
            self.address_line_3,
            self.address_line_4,
            self.address_line_5,
            self.post_code,
            DRUGS_DISPENSED_MARKER[self.drugs_dispensed_marker],
            self.rpp_mileage,
            self.special_district_marker,
            self.walking_units,
            self.residential_institute_code,
        ]


def generate_valid_date():
    random_day = random.randint(1, 14)
    now = datetime.now()
    days_ago = now - timedelta(days=random_day)
    return days_ago


def create_filename(gp_code, ha_cipher, valid_date, file_letter):
    months = "ABCDEFGHIJKL"
    days = "123456789ABCDEFGHIJKLMNOPQRSTUV"
    return f"{gp_code}_GPR4{ha_cipher}1.{months[valid_date.month-1]}{days[valid_date.day-1]}{file_letter}"


def create_record(
    ha_cipher=None,
    nhs_number=None,
    family_name=None,
    given_name=None,
    other_given_name=None,
    title=None,
    gender=None,
    date_of_birth=None,
    address_line_1=None,
    address_line_2=None,
    address_line_3=None,
    address_line_4=None,
    address_line_5=None,
    post_code=None,
    drugs_dispensed_marker=None,
):
    return (
        _record_first_part(
            ha_cipher=ha_cipher,
            nhs_number=nhs_number,
            family_name=family_name,
            given_name=given_name,
            other_given_name=other_given_name,
            title=title,
            gender=gender,
            date_of_birth=date_of_birth,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
        ),
        _record_second_part(
            address_line_3=address_line_3,
            address_line_4=address_line_4,
            address_line_5=address_line_5,
            post_code=post_code,
            drugs_dispensed_marker=drugs_dispensed_marker,
        ),
    )


def _record_first_part(
    ha_cipher,
    nhs_number,
    family_name,
    given_name,
    other_given_name,
    title,
    gender,
    date_of_birth,
    address_line_1,
    address_line_2,
) -> list[str]:
    return RecordPartOne(
        ha_cipher=ha_cipher,
        transaction_id=fake.unique.transaction_id(),
        nhs_number=nhs_number,
        family_name=family_name,
        given_name=given_name,
        other_given_name=other_given_name,
        title=title,
        gender=gender,
        date_of_birth=date_of_birth,
        address_line_1=address_line_1,
        address_line_2=address_line_2,
    ).get_formatted_record()


def _record_second_part(
    address_line_3, address_line_4, address_line_5, post_code, drugs_dispensed_marker
) -> list[str]:
    return RecordPartTwo(
        address_line_3=address_line_3,
        address_line_4=address_line_4,
        address_line_5=address_line_5,
        post_code=post_code,
        drugs_dispensed_marker=drugs_dispensed_marker,
    ).get_formatted_record()
