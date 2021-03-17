# PDS - List reconciliation


## Development installation
```bash
virtualenv env
source env/bin/activate

git clone https://github.com/answer-digital/list-reconciliation
cd list-reconciliation

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
pip install .
```
