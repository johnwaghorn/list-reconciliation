from typing import OrderedDict

from faker import Faker
from faker.providers import BaseProvider, date_time
from pds.address import (
    address_line_1,
    address_line_2,
    address_line_3,
    address_line_4,
    address_line_5,
    post_code,
)
from pds.gp import gp_practice_codes
from pds.name import family_name, given_name, other_given_name


class PDS(BaseProvider):
    def nhs_number(self) -> str:
        return str(self.random_number(digits=10, fix_len=True))

    # Using Faker builtin
    # def date_of_birth(self) -> str:
    #     pass

    def date_of_death(self) -> str:
        # TODO: empty or greater than DATE_OF_BIRTH, small sample
        return ""

    def family_name(self) -> str:
        return self.random_element(family_name)

    def given_name(self) -> str:
        return self.random_element(given_name)

    def other_given_name(self) -> str:
        return self.random_element(other_given_name)

    def title(self) -> str:
        return self.random_element(["MISS", "MRS", "MS", "MR"])

    def gender(self) -> str:
        return self.random_elements(
            elements=OrderedDict(
                [
                    ("Female", 0.51),
                    ("Male", 0.48),
                    ("Not known", 0.005),
                    ("Indeterminate", 0.005),
                ]
            ),
            length=1,
            unique=False,
            use_weighting=True,
        )[0]

    def address_line_1(self) -> str:
        return self.random_element(address_line_1)

    def address_line_2(self) -> str:
        return self.random_element(address_line_2)

    def address_line_3(self) -> str:
        return self.random_element(address_line_3)

    def address_line_4(self) -> str:
        return self.random_element(address_line_4)

    def address_line_5(self) -> str:
        return self.random_element(address_line_5)

    def paf_key(self) -> str:
        return str(self.random_number(digits=8))

    def sensitive_flag(self) -> str:
        return self.random_elements(
            elements=OrderedDict([("U", 0.999), ("V", 0.001), ("REDACTED", 0.001)]),
            length=1,
            unique=False,
            use_weighting=True,
        )[0]

    def primary_care_code(self) -> str:
        return self.random_element(gp_practice_codes)

    def ref_id(self) -> str:
        return ""

    def post_code(self) -> str:
        return self.random_element(post_code)

    def dispensing_flag(self) -> str:
        # TODO: when will dispensing flag not be truthy?
        return "1"


fake = Faker()
Faker.seed(0)
fake.add_provider(date_time)
fake.add_provider(PDS)


def create_filename(row_count):
    return f"pds_data_{row_count}.csv"


def create_patient():
    return {
        "NHS_NUMBER": fake.unique.nhs_number(),
        "DATE_OF_BIRTH": fake.date_of_birth(minimum_age=7).strftime("%Y%m%d"),
        "DATE_OF_DEATH": fake.date_of_death(),
        "FAMILY_NAME": fake.family_name(),
        "GIVEN_NAME": fake.given_name(),
        "OTHER_GIVEN_NAME": fake.other_given_name(),
        "TITLE": fake.title(),
        "GENDER": fake.gender(),
        "ADDRESS_LINE_1": fake.address_line_1(),
        "ADDRESS_LINE_2": fake.address_line_2(),
        "ADDRESS_LINE_3": fake.address_line_3(),
        "ADDRESS_LINE_4": fake.address_line_4(),
        "ADDRESS_LINE_5": fake.address_line_5(),
        "PAF_KEY": fake.unique.paf_key(),
        "SENSITIVE_FLAG": fake.sensitive_flag(),
        "PRIMARY_CARE_CODE": fake.primary_care_code(),
        "REF_ID": fake.ref_id(),
        "POST_CODE": fake.post_code(),
        "DISPENSING_FLAG": fake.dispensing_flag(),
    }
