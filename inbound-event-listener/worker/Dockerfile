FROM python:3.8-alpine

RUN apk update && apk add bash make g++ gcc

WORKDIR /worker

COPY ./ /worker/

RUN pip install -r /worker/requirements.txt

ENTRYPOINT [ "/worker/docker/entrypoint.sh" ]
CMD [ "python", "-m", "src.worker" ]
