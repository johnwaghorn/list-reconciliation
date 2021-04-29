# PDS - List reconciliation


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


## Databricks libraries
Setup secrets for accessing S3 bucket

```bash
databricks secrets put --scope aws --key aws_public_key
databricks secrets put --scope aws --key aws_private_key
```

Build and upload python egg to cluster

```bash
python setup.py bdist_egg
```

Once the egg has been created it must be uploaded to Databricks as a [library](https://docs.databricks.com/libraries/index.html) which can then be imported as normal.

```python
from listrec.utils import save_to_s3_csv
...
```


## Terraform usage
Note: The `-chdir` command isn't required if you are in the `terraform` directory

```bash
terraform -chdir=terraform\ init
```

Your AWS credentials need to be up to date before being able to `apply`

```bash
terraform -chdir=terraform\ apply
```