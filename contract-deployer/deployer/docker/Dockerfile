FROM node:10-alpine

WORKDIR /deployer

RUN apk update && \
  apk add --no-cache git bash make gcc g++ python3 zip && \
  mkdir contract && \
  chown -R node /deployer

COPY package*.json ./

USER node

RUN npm install

COPY ./ ./

ENTRYPOINT  /deployer/docker/entrypoint.sh
