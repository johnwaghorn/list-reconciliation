from dataclasses import dataclass

from dps_pds.faker import DPSPDSProvider
from faker import Faker

fake = Faker()
Faker.seed(0)
fake.add_provider(DPSPDSProvider)


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
