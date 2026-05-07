.PHONY: test check terraform integration

test:
	python3 -m unittest discover -s tests -v

check: test
	python3 tools/check_repo.py
	bash -n bootstrap/startup.sh

terraform:
	terraform -chdir=terraform fmt -check -recursive
	terraform -chdir=terraform init -backend=false -input=false
	terraform -chdir=terraform validate
	terraform -chdir=terraform test

integration:
	python3 tools/fetch_test_runtime.py
	python3 tests/integration.py --kafka-home .local/kafka_2.13-4.1.2 --jmx-jar .local/jmx.jar
