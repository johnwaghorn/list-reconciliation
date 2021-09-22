from faker.providers import BaseProvider


class GPProvider(BaseProvider):
    def transaction_id(self):
        return str(self.random_number(digits=6, fix_len=True))

    def patient_gender(self):
        return str(self.random_element([1, 2, 3, 3, 9]))
