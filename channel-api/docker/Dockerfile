FROM node:alpine

WORKDIR /channel-api

RUN apk update &&\
  apk add bash curl gcc g++ make python3 python3-dev &&\
  curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python3

COPY poetry.lock  pyproject.toml ./

RUN source ~/.poetry/env && poetry config virtualenvs.create false && poetry install --no-root

COPY package.json package-lock.json ./

RUN npm ci

COPY ./ ./

ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["./docker/entrypoint.sh"]
