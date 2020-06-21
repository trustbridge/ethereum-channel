.PHONY: run-fg
.ONESHELL:
run-fg: clean-contract-build
	@ docker-compose up --build --remove-orphans


.PHONY: run
.ONESHELL:
run: clean-contract-build
	@ docker-compose up --build --remove-orphans -d


.PHONY: clean-contract-build
.ONESHELL:
clean-contract-build:
	@ rm -rf contract/build
	@ rm -rf deployer/contract-deployment/build

.PHONY: clean
.ONESHELL:
clean: clean-contract-build
	@ rm -rf contract/build
	@ docker-compose down --rmi all --volumes


.PHONY: build
.ONESHELL:
build:
	@ docker-compose build --no-cache


.PHONY: shell-deployer
.ONESHELL:
shell-deployer:
	@ docker-compose exec deployer /bin/bash


.PHONY: shell-ganache-cli
.ONESHELL:
shell-ganache-cli:
	@ docker-compose exec ganache-cli /bin/sh
