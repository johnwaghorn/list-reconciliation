deployment_environment ?= dev
terraform_workspace ?= default

all: python-package init apply
test: integrationtests unittest

python-package:
	rm -r ./lambda_layer || true
	mkdir -p ./lambda_layer/python/lib/python3.8/site-packages
	echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin || true
	docker run --rm -v $(PWD):/var/task -u $(shell id -u):$(shell id -g) -w="/var/task/" public.ecr.aws/sam/build-python3.8 /bin/python3 -m pip install -r requirements.txt -t ./lambda_layer/python/lib/python3.8/site-packages
	cp -r ./packages/* ./lambda_layer/python/lib/python3.8/site-packages

init:
	terraform -chdir=./terraform/environment/${deployment_environment} init

workspace:
	terraform -chdir=./terraform/environment/${deployment_environment}  workspace select ${terraform_workspace} || terraform -chdir=./terraform/environment/${deployment_environment}  workspace new ${terraform_workspace}
	terraform -chdir=./terraform/environment/${deployment_environment}  workspace show

workspace-delete:
	terraform -chdir=./terraform/environment/${deployment_environment} workspace select default
	terraform -chdir=./terraform/environment/${deployment_environment} workspace delete ${terraform_workspace}

plan:
	terraform -chdir=./terraform/environment/${deployment_environment} plan

apply:
	terraform -chdir=terraform/environment/${deployment_environment} apply -auto-approve
	rm -f ./output.json || true
	terraform -chdir=terraform/environment/${deployment_environment} output -json > ./output.json

destroy:
	terraform -chdir=terraform/environment/${deployment_environment} destroy

integrationtest-deps:
	pip install -r test_requirements.txt
	pip install -e .

integrationtests:
	cd ./test/integrationtests && gauge run --tags "!wip" ./specs

unittests:
	pytest --ignore=test/integrationtests
