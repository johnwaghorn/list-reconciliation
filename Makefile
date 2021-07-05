#
# Variables
#

branch := $(shell git branch --show-current)
env ?= dev
stack ?= list-reconciliation

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
	terraform -chdir=./terraform/stacks/${stack} init
	terraform -chdir=./terraform/stacks/${stack} get -update

workspace:
	terraform -chdir=./terraform/stacks/${stack} workspace select ${env} || terraform -chdir=./terraform/stacks/${stack} workspace new ${env}
	terraform -chdir=./terraform/stacks/${stack} workspace show

workspace-delete:
	terraform -chdir=./terraform/stacks/${stack} workspace select default
	terraform -chdir=./terraform/stacks/${stack} workspace delete ${env}

plan:
	terraform -chdir=./terraform/stacks/${stack} plan

apply:
	terraform -chdir=./terraform/stacks/${stack} apply -auto-approve
	rm -f ./terraform_outputs_${stack}.json|| true
	terraform -chdir=./terraform/stacks/${stack} output -json > ./terraform_outputs_${stack}.json

destroy:
	terraform -chdir=./terraform/stacks/${stack} destroy -auto-approve

# Testing
validate:
	terraform -chdir=./terraform/stacks/${stack} validate

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
	@echo $(shell if echo ${branch} | grep -qEo '^(\w+/)?(\w+[-_])?[0-9]+'; then echo ${branch} | grep -Eo '^(\w+/)?(\w+[-_])?[0-9]+' | grep -Eo '(\w+[-])?[0-9]+' | tr "[:lower:]" "[:upper:]"; else echo ${branch}; fi)-$(shell echo ${branch} | sha1sum | head -c 8)

hooks:
	pre-commit install
	pre-commit install --hook-type prepare-commit-msg
