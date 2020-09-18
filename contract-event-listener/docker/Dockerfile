FROM python:3.8-alpine

RUN apk update && apk add bash make g++ gcc

WORKDIR /worker

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY ./ ./

ENTRYPOINT ["/worker/docker/entrypoint.sh"]
