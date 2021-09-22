import dps_pds.gp_practices
from faker.providers import BaseProvider


class DPSPDSProvider(BaseProvider):
    def nhs_number(self):
        return self.random_number(digits=10, fix_len=True)

    def gp_practice(self):
        return self.random_element(dps_pds.gp_practices.ref)

    def dispensing_flag(self):
        return self.random_element([0, 1])
