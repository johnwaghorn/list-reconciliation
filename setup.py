from setuptools import find_packages, setup

setup(
    name="listrec",
    version="0.0.1",
    description="List Reconciliation",
    author="Answer Digital",
    license="",
    packages=find_packages(where="./packages"),
    package_dir={"": "packages"},
    install_requires=["pipenv"],
    entry_points={"console_scripts": ["gpextract = gp_file_parser.main:main"]},
)
