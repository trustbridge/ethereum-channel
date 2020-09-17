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
