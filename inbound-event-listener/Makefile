.PHONY: run-fg
.ONESHELL:
run-fg:
	@ docker-compose up --build --remove-orphans


.PHONY: clean-blockhain
clean-blockhain:
	@ rm -rf ganache-cli/database
	@ mkdir ganache-cli/database


.PHONY: clean
.ONESHELL:
clean: clean-blockhain
	@ docker-compose down --rmi all --volumes


.PHONY: run
.ONESHELL:
run:
	@ docker-compose up --build --remove-orphans -d


.PHONY: build
.ONESHELL:
build:
	@ docker-compose build --no-cache


.PHONY: shell-worker
.ONESHELL:
shell-worker:
	@ docker-compose exec worker /bin/bash


.PHONY: shell-truffle
.ONESHELL:
shell-truffle:
	@ docker-compose exec truffle /bin/bash


.PHONY: shell-ganache-cli
.ONESHELL:
shell-ganache-cli:
	@ docker-compose exec ganache-cli /bin/sh
