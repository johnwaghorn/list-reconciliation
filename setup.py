from setuptools import setup, find_packages

with open("requirements.txt") as f:
    dependencies = [r.strip() for r in f.readlines()]

setup(
    name="listrec",
    version="0.0.1",
    description="List Reconciliation",
    author="Answer Digital",
    license="",
    packages=find_packages(where="./packages"),
    package_dir={"": "packages"},
    install_requires=dependencies,
    entry_points={"console_scripts": ["gpextract = gp_file_parser.main:main"]},
)
