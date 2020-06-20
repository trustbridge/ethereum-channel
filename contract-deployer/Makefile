.PHONY: run-fg
.ONESHELL:
run-fg:
	@ docker-compose up --build --remove-orphans


.PHONY: run
.ONESHELL:
run:
	@ docker-compose up --build --remove-orphans -d


.PHONY: clean
.ONESHELL:
clean: clean-blockchain
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
