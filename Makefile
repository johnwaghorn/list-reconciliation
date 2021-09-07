#
# Variables
#

branch := $(shell git branch --show-current)
env ?= dev
stack ?= list-reconciliation
mesh_post_office_lambda ?= LR_25_mesh_post_office-prod
job_cleanup_lambda ?= LR_27_job_cleanup-prod
job_id ?= 00000000-0000-0000-0000-000000000000

#
# Shared rules
#

all: python-package init apply
test: integrationtests unittests
format: fmt black
python-package: packages-layer dependencies-layer

#
# Python
#

# Dependencies
python-deps:
	pipenv install --dev --ignore-pipfile

# Packaging
dependencies-layer:
	rm -r ./dependencies_layer || true
	mkdir -p ./dependencies_layer/python/
	pipenv lock -r | pipenv run pip install --cache-dir .pip_cache --target ./dependencies_layer/python/ -r /dev/stdin

packages-layer:
	rm -r ./packages_layer || true
	mkdir -p ./packages_layer/python/
	cp -r ./packages/* ./packages_layer/python/

compress-packages:
	tar czf ./dependencies_layer.tgz ./dependencies_layer/*
	tar czf ./packages_layer.tgz ./packages_layer/*

uncompress-packages:
	tar xzf ./dependencies_layer.tgz ./dependencies_layer/
	tar xzf ./packages_layer.tgz ./packages_layer/

# Testing
unittests:
	pytest -v --doctest-modules --cov=packages --html=report/reports.html

syntax-check:
	flake8 --count --select=E9,F63,F7,F82 --show-source --statistics lambdas/ packages/ test/

error-check:
	flake8 --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics lambdas/ packages/ test/

# Formatting
black:
	python -m black --line-length 100 lambdas/ packages/ test/

black-check:
	python -m black --line-length 100 --check lambdas/ packages/ test/

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

apply-lambda: packages-layer
	terraform -chdir=./terraform/stacks/list-reconciliation apply -auto-approve --target=module.${lambda}

output:
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

# Running
integrationtests:
	gauge run --verbose --tags "!wip,e2e" ./test/integrationtests/specs

integrationtests-preprod:
	gauge run --verbose --tags "!wip,preprod" ./test/integrationtests/specs

# TODO rename this and replace above once migrated
behave-integration-tests:
	behave ./test/integration


#
# Security
#

tfsec:
	tfsec ./terraform/stacks/${stack}

#
# Utilities
#

get-branch-env:
	@echo $(shell if echo ${branch} | grep -qo 'develop'; then \
		echo "test"; \
	elif echo ${branch} | grep -qo 'master'; then \
		echo "preprod"; \
	elif echo ${branch} | grep -qEo '^(\w+/)?(\w+[-_])?[0-9]+'; then \
		ENV_BRANCH_NAME=$$(echo ${branch} | grep -Eo '^(\w+/)?(\w+[-_])?[0-9]+' | grep -Eo '(\w+[-])?[0-9]+' | tr "[:lower:]" "[:upper:]"); \
		ENV_HASH=$$(echo ${branch} | sha1sum | head -c 8); \
		echo "$${ENV_BRANCH_NAME}-$${ENV_HASH}"; \
	else \
		ENV_BRANCH_NAME=$$(echo ${branch} | sed -e 's/_/-/g' -e 's/\./-/g' | head -c 10); \
		ENV_HASH=$$(echo ${branch} | sha1sum | head -c 8); \
		echo "$${ENV_BRANCH_NAME}-$${ENV_HASH}"; \
	fi)

hooks:
	pre-commit install
	pre-commit install --hook-type prepare-commit-msg

#
# Operations
#

# Mesh Post Office Lambda
open-mesh-post-office:
	@aws ssm put-parameter --name /${mesh_post_office_lambda}/mesh_post_office_open --type "String" --value "True" --overwrite > /dev/null
	@aws lambda delete-function-concurrency --function-name ${mesh_post_office_lambda} > /dev/null
	@aws ssm get-parameter --name /${mesh_post_office_lambda}/mesh_post_office_open

close-mesh-post-office:
	@aws ssm put-parameter --name /${mesh_post_office_lambda}/mesh_post_office_open --type "String" --value "False" --overwrite > /dev/null
	@aws lambda put-function-concurrency --function-name ${mesh_post_office_lambda} --reserved-concurrent-executions 0 > /dev/null
	@aws ssm get-parameter --name /${mesh_post_office_lambda}/mesh_post_office_open

# Job Cleanup Lambda
job-cleanup:
	@aws lambda invoke --function-name ${job_cleanup_lambda} --cli-binary-format raw-in-base64-out --payload '{"job_id":"${job_id}"}' --log-type Tail ${job_cleanup_lambda}_${job_id}.log > /dev/null
	@cat ${job_cleanup_lambda}_${job_id}.log
# Echo a newline so we don't mess up the users terminal
	@echo
