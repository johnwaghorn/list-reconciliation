import dps_pds.gp_practices
from faker import Faker
from faker.providers import BaseProvider


class NHSNumber(BaseProvider):
    def nhs_number(self):
        return self.random_number(digits=10, fix_len=True)


class GPPractice(BaseProvider):
    def gp_practice(self):
        return self.random_element(dps_pds.gp_practices.ref)


class DispensingFlag(BaseProvider):
    def dispensing_flag(self):
        return self.random_element([0, 1])


def create_filename(row_count):
    return f"dps_pds_data_{row_count}.csv"


def create_patient():
    fake = Faker()
    fake.add_provider(NHSNumber)
    fake.add_provider(GPPractice)
    fake.add_provider(DispensingFlag)
    return [fake.nhs_number(), fake.gp_practice(), fake.dispensing_flag()]
