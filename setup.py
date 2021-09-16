from setuptools import find_packages, setup

setup(
    name="list-reconciliation",
    version="0.1.0",
    description="List Reconciliation",
    author="NHS Digital",
    license="",
    packages=find_packages(where="./packages"),
    package_dir={"": "packages"},
    install_requires=["pipenv"],
)
