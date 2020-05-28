FROM python:3.8-alpine

RUN apk update && apk add bash make g++ gcc

WORKDIR /worker

COPY docker/stage/install/python docker/stage/install/python

RUN docker/stage/install/python/install.sh 

ENTRYPOINT /worker/docker/entrypoint.sh
