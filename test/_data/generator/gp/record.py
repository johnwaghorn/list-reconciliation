from dataclasses import dataclass

from faker import Faker
from gp.faker import GPProvider

fake = Faker()
Faker.seed(0)
fake.add_provider(GPProvider)


@dataclass
class Record:
    record_identifier_1: str = "DOW"
    record_part_1: str = "1"
    gp_practice_codes: str = "1111111,1234"
    ha_cipher: str = "LNA"
    export_date: str = "20210919"  # TODO always be yesterday?
    export_time: str = "1500"
    transaction_id: str = fake.unique.transaction_id()
    nhs_number: str = ""
    family_name: str = ""
    given_name: str = ""
    other_given_name: str = ""
    title: str = ""
    gender: str = fake.patient_gender()
    date_of_birth: str = ""
    address_line_1: str = ""
    address_line_2: str = ""
    record_identifier_2: str = "DOW"
    record_part_2: str = "2"
    address_line_3: str = ""
    address_line_4: str = ""
    address_line_5: str = ""
    post_code: str = ""
    drugs_dispensed_marker: str = ""
    rpp_mileage: str = ""
    special_district_marker: str = ""
    walking_units: str = ""
    residential_institute_code: str = ""

    GENDER = {
        "Male": "1",
        "Female": "2",
        "Not known": "0",
        "Indeterminate": "0",
        "Not Specified": "9",
    }
    DRUGS_DISPENSED_MARKER = {"1": "Y", "0": "N"}

    def get(self):
        return [
            self.record_identifier_1,
            self.record_part_1,
            self.gp_practice_codes,
            self.ha_cipher,
            self.export_date,
            self.export_time,
            self.transaction_id,
            self.nhs_number,
            self.family_name.upper(),
            self.given_name.upper(),
            self.other_given_name.upper(),
            self.title,
            self.GENDER[self.gender],
            self.date_of_birth,
            self.address_line_1.upper(),
            self.address_line_2.upper(),
            self.record_identifier_2,
            self.record_part_2,
            self.address_line_3.upper(),
            self.address_line_4.upper(),
            self.address_line_5.upper(),
            self.post_code,
            self.DRUGS_DISPENSED_MARKER[self.drugs_dispensed_marker],
            self.rpp_mileage,
            self.special_district_marker,
            self.walking_units,
            self.residential_institute_code,
        ]
