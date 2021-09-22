from pds import PDSData
from storage import LocalStorage


class Generator:
    def main(self):
        size = 1_000_000
        # file = GPData()
        # file = DPSPDSData()
        file = PDSData()
        storage = LocalStorage()
        # storage = DynamoDBStorage()

        storage.store(file.create_file(size))


if __name__ == "__main__":
    gen = Generator()
    gen.main()
