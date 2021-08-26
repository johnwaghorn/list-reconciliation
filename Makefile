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

# Packaging
packages-layer:
	rm -r ./packages_layer || true
	mkdir -p ./packages_layer/python/
	cp -r ./packages/* ./packages_layer/python/

dependencies-layer:
	rm -r ./dependencies_layer || true
	mkdir -p ./dependencies_layer/python/
	echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin || true
	docker run --rm -v $(PWD):/var/task -u $(shell id -u):$(shell id -g) -w="/var/task/" --entrypoint python public.ecr.aws/lambda/python:3.9 -m pip install --cache-dir .pip_cache -r requirements.txt -t ./dependencies_layer/python/

# Testing
unittests:
	pytest -v --doctest-modules --cov=packages

# Formatting
black:
	python -m black --line-length 100 .

black-check:
	python -m black --line-length 100 --check .

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
	terraform -chdir=./terraform/stacks/list-reconciliation apply -auto-approve --target=module.lambda.module.${lambda}

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

# Dependencies
integrationtest-deps:
	pip install -r test_requirements.txt
	pip install -e .

# Running
integrationtests:
	cd ./test/integrationtests && gauge run --verbose --tags "!wip,e2e" ./specs

integrationtests-preprod:
	cd ./test/integrationtests && gauge run --verbose --tags "!wip,preprod" ./specs

#
# Utilities
#

get-branch-id:
	@echo $(shell if echo ${branch} | grep -qEo '^(\w+/)?(\w+[-_])?[0-9]+'; then echo ${branch} | grep -Eo '^(\w+/)?(\w+[-_])?[0-9]+' | grep -Eo '(\w+[-])?[0-9]+' | tr "[:lower:]" "[:upper:]"; else echo ${branch} | sed -e 's/_/-/g' -e 's/\./-/g' | head -c 10; fi)-$(shell echo ${branch} | sha1sum | head -c 8)

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
