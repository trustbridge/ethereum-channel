FROM node:10-alpine

WORKDIR /deployer

RUN apk update && \
  apk add --no-cache git bash make gcc g++ python3 zip && \
  mkdir contract && \
  chown -R node /deployer

USER node

ENV NPM_CONFIG_PREFIX=/home/node/.npm-global
ENV PATH=/home/node/.npm-global/bin:$PATH

RUN npm install --global \
  chai \
  mocha \
  pino \
  pino-pretty \
  md5 \
  truffle \
  @truffle/hdwallet-provider \
  aws-sdk \
  lodash \
  @babel/core@^7.0.0-0

COPY ./ ./

ENTRYPOINT  /deployer/docker/entrypoint.sh
