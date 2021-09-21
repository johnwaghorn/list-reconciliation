from dataclasses import dataclass

import dps_pds.gp_practices
from faker import Faker
from faker.providers import BaseProvider


class DPSPDS(BaseProvider):
    def nhs_number(self):
        return self.random_number(digits=10, fix_len=True)

    def gp_practice(self):
        return self.random_element(dps_pds.gp_practices.ref)

    def dispensing_flag(self):
        return self.random_element([0, 1])


fake = Faker()
Faker.seed(0)
fake.add_provider(DPSPDS)


@dataclass
class Record:
    nhs_number: str = fake.nhs_number()
    gp_practice: str = fake.gp_practice()
    dispensing_flag: str = fake.dispensing_flag()

    def get(self):
        return [
            self.nhs_number,
            self.gp_practice,
            self.dispensing_flag,
        ]


def create_filename(name):
    return f"dps_pds_data_{name}.csv"
