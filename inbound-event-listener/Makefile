.PHONY: run-fg
.ONESHELL:
run-fg:
	@ docker-compose up --build --remove-orphans


.PHONY: clean-blockchain
clean-blockchain:
	@ rm -rf worker/listener-blocks-log
	@ mkdir worker/listener-blocks-log
	@ rm -rf ganache-cli/database
	@ mkdir ganache-cli/database


.PHONY: clean
.ONESHELL:
clean: clean-blockchain
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


.PHONY: shell-truffle-console
.ONESHELL:
shell-truffle-console:
	@ docker-compose exec truffle /bin/bash -c "cd /truffle/contracts/EventEmitter && truffle console"


.PHONY: shell-ganache-cli
.ONESHELL:
shell-ganache-cli:
	@ docker-compose exec ganache-cli /bin/sh
