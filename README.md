# PDS - List reconciliation

* [Development installation](#development-installation)
* [Deployment Installation](#deployment-installation)
* [Terraform usage](#terraform-usage)
    + [Pre-requisite for Windows users only](#pre-requisite-for-windows-users-only)
    + [Deploying Infrastructure](#deploying-infrastructure)
    + [Deploying environment on AWS](#deploying-environment-on-aws)
* [Comparison engine](#Comparison-engine)
* [LeftRecord and RightRecord](#leftrecord-and-rightrecord)
* [Comparison functions](#comparison-functions)

## Development installation

```bash
virtualenv env
source env/bin/activate

git clone https://github.com/answer-digital/list-reconciliation
cd list-reconciliation
pip install -r requirements.txt

# Install package in editable mode
pip install -e .

# Install test dependencies
pip install -r test_requirements.txt

# Run tests
pytest

# Run the program with two input files from the same extract group
gpextract /tmp/output GPR4LNA1.C7A GPR4LNA1.C7B -t 0 -r
```

## Deployment Installation

```bash
virtualenv env
source env/bin/activate

git clone https://github.com/answer-digital/list-reconciliation
cd list-reconciliation
pip install -r requirements.txt
pip install .
```

## Terraform usage

Install _terraform_ from [here](https://www.terraform.io/downloads.html) as per developers platform

### Pre-requisite for Windows users only

1. Install Ubuntu on using [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
2. Install make on WSL (`sudo apt-get install make`)
3. If you wish to use WSL entirely for deployment then install Terraform on WSL as well.

### Deploying Infrastructure

Note: The `-chdir` command isn't required if you are in the `terraform` directory

Create a new workspace (if it is not created already) by using following command

    terraform -chdir=terraform/environment/dev workspace new <workspace-name>

This will create a new and switch workspace locally in your machine. To check if it is created

      terraform -chdir=terraform/environment/dev workspace list

To switch to new workspace

    terraform -chdir=terraform/environment/dev workspace select <workspace-name> 

### Initialise Terraform

      make init 

### Terraform Plan

This outputs the `json` format of what resources are going to be created

      make plan

Note: if you are executing `make plan` first time , ensure to run `make init` first

### Deploying environment on AWS

      make deploy

_Note: You may have to confirm by typing 'Yes' before it creates resources on AWS, This updates the resources if there
is any change_in terraform script

### Deleting Resources on AWS :

      make destroy

## Comparison engine

The core comparison engine provides a lightweight framework for defining representations of records and one or more
comparison functions to apply to the records to produce a result. The left and right records, and comparison functions
are defined in a regular python module, while usage of the framework allows the objects to be collected and handled
using introspection at runtime.

## LeftRecord and RightRecord

These two special classes must be subclassed exactly once, each one representing a record to be compared to the other.
Like other ORMs, columns are defined as class attributes. This is the only point at which the user references the real
column names as found in the dictionary representing the record. Once defined, columns are referred to by the attribute
name within square brackets.

```python
from datetime import datetime
from comparison_engine.schema import LeftRecord, RightRecord, IntegerColumn, StringColumn, DateTimeColumn


class GPRecord(LeftRecord):
    ID = IntegerColumn("id", primary_key=True)
    DATE_OF_BIRTH = DateTimeColumn(
        "date_of_birth", format=lambda x: datetime.strptime(str(x), "%Y-%m-%d")
    )
    NAME = StringColumn(["name1", "name2"], format=lambda x: " ".join(x).strip())
    SURNAME = StringColumn("surname")


class PDSRecord(RightRecord):
    ID = IntegerColumn("id", primary_key=True)
    DATE_OF_BIRTH = DateTimeColumn("dob", format=lambda x: datetime.strptime(str(x), "%Y%m%d"))
    NAME = StringColumn("forename")
    SURNAME = StringColumn("surname")
```

## Comparison functions

These functions are defined by the user. There must be exactly 2 arguments, `left` and `right`, and within the function
the user sets out the logic to compare both sides, referencing the previously defined class attributes as the column
names. Any comparison functions must be decorated with the `comparison` decorator for the function to be applied to the
record pair. The `comparison` decorator must have a unique ID as an argument. The comparison function must return a
boolean; `True` if the result of the comparison indicates that the record needs further action (i.e. the values are not
equal); `False` if the values are equal and no further action is needed.

```python
from comparison_engine.core import comparison


@comparison('ABC123')
def date_of_birth_not_equal(left: LeftRecord, right: RightRecord):
    return left["DATE_OF_BIRTH"] != right["DATE_OF_BIRTH"]
```

```

