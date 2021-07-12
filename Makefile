#
# Variables
#

env ?= dev

#
# Shared rules
#

all: python-package init apply
test: integrationtests unittests
format: fmt black

#
# Python
#

# Packaging
python-package:
	rm -r ./lambda_layer || true
	mkdir -p ./lambda_layer/python/lib/python3.8/site-packages
	echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin || true
	docker run --rm -v $(PWD):/var/task -u $(shell id -u):$(shell id -g) -w="/var/task/" public.ecr.aws/sam/build-python3.8 /bin/python3 -m pip install -r requirements.txt -t ./lambda_layer/python/lib/python3.8/site-packages
	cp -r ./packages/* ./lambda_layer/python/lib/python3.8/site-packages

# Testing
unittests:
	pytest --ignore=test/integrationtests

# Formating
black:
	python -m black --line-length 100 .

black-check:
	# Remove always true once code is formatted
	python -m black --line-length 100 --check . || true

#
# Terraform
#

# Executing
init:
	terraform -chdir=./terraform/stacks/list-reconciliation init

workspace:
	terraform -chdir=./terraform/stacks/list-reconciliation workspace select ${env} || terraform -chdir=./terraform/stacks/list-reconciliation workspace new ${env}
	terraform -chdir=./terraform/stacks/list-reconciliation workspace show

workspace-delete:
	terraform -chdir=./terraform/stacks/list-reconciliation workspace select default
	terraform -chdir=./terraform/stacks/list-reconciliation workspace delete ${env}

plan:
	terraform -chdir=./terraform/stacks/list-reconciliation plan

apply:
	terraform -chdir=./terraform/stacks/list-reconciliation apply -auto-approve
	rm -f ./output.json || true
	terraform -chdir=./terraform/stacks/list-reconciliation output -json > ./output.json

destroy:
	terraform -chdir=./terraform/stacks/list-reconciliation destroy -auto-approve

# Testing
validate:
	terraform -chdir=./terraform/stacks/list-reconciliation validate

# Formatting
fmt:
	terraform -chdir=./terraform/ fmt -recursive

fmt-check:
	terraform -chdir=./terraform/ fmt -recursive -check

#
# Testing
#

# Dependencies
integrationtest-deps:
	pip install -r test_requirements.txt
	pip install -e .

# Running
integrationtests:
	cd ./test/integrationtests && gauge run --tags "!wip" ./specs

#
# Utilities
#

get-branch-id:
	@echo $(shell git branch --show-current | grep -Eo '^(\w+/)?(\w+[-_])?[0-9]+' | grep -Eo '(\w+[-])?[0-9]+' | tr "[:lower:]" "[:upper:]")-$(shell git branch --show-current | sha1sum | head -c 8)

hooks:
	pre-commit install
	pre-commit install --hook-type prepare-commit-msg
