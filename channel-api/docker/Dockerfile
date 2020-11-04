FROM python:3.8

WORKDIR /channel-api

RUN apt-get update && \
  apt-get install -y bash make gcc g++ nmap && \
  rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY ./ ./

ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["./docker/entrypoint.sh"]
