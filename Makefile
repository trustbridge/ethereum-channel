.PHONY: run
.ONESHELL:
run:
	@ docker-compose up --build --remove-orphans --renew-anon-volumes

.PHONY: run-on-servers
.ONESHELL:
run-on-servers:
	@ docker-compose -f docker-compose.servers.yml up --build --remove-orphans --renew-anon-volumes

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


.PHONY: shell-deployer-participant-ja
.ONESHELL:
shell-deployer-participant-ja:
	@ docker-compose exec deployer-participant-ja /bin/bash


.PHONY: shell-ganache-cli
.ONESHELL:
shell-ganache-cli:
	@ docker-compose exec ganache-cli /bin/sh


.PHONY: shell-localstack
.ONESHELL:
shell-localstack:
	@ docker-compose exec localstack /bin/sh


.PHONY: shell-channel-api
.ONESHELL:
shell-channel-api:
	@ docker-compose exec channel-api /bin/bash


.PHONY: shell-websub-hub
.ONESHELL:
shell-websub-hub:
	@ docker-compose exec websub-hub /bin/bash
