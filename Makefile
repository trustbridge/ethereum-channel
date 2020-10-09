.PHONY: run
.ONESHELL:
run:
	export YAML_CONFIG_FILE_VALUE_AU="$$(cat contract-event-listener-au.yml)"
	export YAML_CONFIG_FILE_VALUE_GB="$$(cat contract-event-listener-gb.yml)"
	cat docker-compose.base.yml docker-compose.system.yml > docker-compose.yml
	docker-compose down -v
	docker-compose up --build --remove-orphans --renew-anon-volumes


.PHONY: run-contract-event-listener
.ONESHELL:
run-contract-event-listener:
	cat docker-compose.base.yml docker-compose.contract-event-listener.yml > docker-compose.yml
	docker-compose down -v
	docker-compose up --build --remove-orphans --renew-anon-volumes


.PHONY: run-channel-api
.ONESHELL:
run-channel-api:
	cat docker-compose.base.yml docker-compose.channel-api.yml > docker-compose.yml
	docker-compose down -v
	docker-compose up --build --remove-orphans --renew-anon-volumes


.PHONY: stop
.ONESHELL:
stop:
	@ docker-compose down

.PHONY: clean
.ONESHELL:
clean:
	@ docker-compose down --rmi all --volumes

.PHONY: build
.ONESHELL:
build:
	@ docker-compose build --no-cache


.PHONY: shell-ganache-cli
.ONESHELL:
shell-ganache-cli:
	@ docker-compose exec ganache-cli /bin/sh


.PHONY: shell-localstack
.ONESHELL:
shell-localstack:
	@ docker-compose exec localstack /bin/sh


.PHONY: shell-deployer-participant-au
.ONESHELL:
shell-deployer-participant-au:
	@ docker-compose exec deployer-participant-au /bin/bash


.PHONY: shell-deployer-participant-gb
.ONESHELL:
shell-deployer-participant-gb:
	@ docker-compose exec deployer-participant-gb /bin/bash


.PHONY: shell-channel-api
.ONESHELL:
shell-channel-api:
	@ docker-compose exec channel-api /bin/bash


.PHONY: shell-channel-api-au
.ONESHELL:
shell-channel-api-au:
	@ docker-compose exec channel-api-au /bin/bash


.PHONY: shell-channel-api-gb
.ONESHELL:
shell-channel-api-gb:
	@ docker-compose exec channel-api-gb /bin/bash


.PHONY: shell-websub-hub-au
.ONESHELL:
shell-websub-hub-au:
	@ docker-compose exec websub-hub-au /bin/bash


.PHONY: shell-websub-hub-gb
.ONESHELL:
shell-websub-hub-gb:
	@ docker-compose exec websub-hub-gb /bin/bash


.PHONY: shell-contract-event-listener-au
.ONESHELL:
shell-contract-event-listener-au:
	@ docker-compose exec contract-event-listener-au /bin/bash


.PHONY: shell-contract-event-listener-gb
.ONESHELL:
shell-contract-event-listener-gb:
	@ docker-compose exec contract-event-listener-gb /bin/bash

.PHONY: shell-contract-event-listener-contract
.ONESHELL:
shell-contract-event-listener-contract:
	@ docker-compose exec contract-event-listener-contract /bin/bash

.PHONY: shell-contract-event-listener
.ONESHELL:
shell-contract-event-listener:
	@ docker-compose exec contract-event-listener /bin/bash
