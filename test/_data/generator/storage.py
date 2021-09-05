import os
from abc import ABC, abstractmethod

# TODO put somewhere better
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


class Storage(ABC):
    """Abstract Storage Class"""

    @abstractmethod
    def list():
        """list stored files"""

    @abstractmethod
    def store(file):
        """store a file"""

    @abstractmethod
    def retrieve(file):
        """retrive a file"""


class LocalStorage(Storage):
    def list(self):
        pass

    def store(self, file):
        name = os.path.basename(file)
        os.rename(file, os.path.join(OUTPUT_DIR, name))

    def retrieve(self, file):
        pass


class S3Storage(Storage):
    def list(self):
        pass

    def store(self, file):
        pass

    def retrieve(self, file):
        pass
