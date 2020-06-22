FROM node:alpine


WORKDIR /truffle

ARG DOCUMENT_STORE_MASTER_COMMIT

RUN apk update && apk add --no-cache git bash make gcc g++

USER node

ENV PATH=~/.npm-global/bin:$PATH
ENV NPM_CONFIG_PREFIX=~/.npm-global

RUN npm install -g truffle

COPY entrypoint.sh entrypoint.sh

ENTRYPOINT  /truffle/entrypoint.sh
