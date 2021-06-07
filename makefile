deployment_environment ?= dev
init:
	rm -r ./lambda_layer || true
	mkdir -p ./lambda_layer/python/lib/python3.8/site-packages
	docker run --rm -v $(PWD):/var/task -w="/var/task/" public.ecr.aws/sam/build-python3.8 /bin/python3 -m pip install -r requirements.txt -t ./lambda_layer/python/lib/python3.8/site-packages
	cp -r ./packages/* ./lambda_layer/python/lib/python3.8/site-packages
	terraform -chdir=terraform/environment/${deployment_environment} init

plan:
	terraform -chdir=terraform/environment/${deployment_environment} plan

deploy:
	terraform -chdir=terraform/environment/${deployment_environment} apply

destroy:
	terraform -chdir=terraform/environment/${deployment_environment} destroy
