import os

from storage.locations import LOCAL_OUTPUT_DIR


class LocalStorage:
    def list(self):
        pass

    def store(self, tmp_file):
        name = os.path.basename(tmp_file)
        os.rename(tmp_file, os.path.join(LOCAL_OUTPUT_DIR, name))

    def retrieve(self, file):
        pass
