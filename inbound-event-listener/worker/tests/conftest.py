import os
import boto3
import pytest


AWS_RESOURCE_CONFIG = dict(
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name='us-east-1',
    endpoint_url='http://ec-iel-localstack:10001'
)


@pytest.fixture(scope='session')
def queue():
    queue_url = [
        'http://ec-iel-localstack:10001/queue/queue-1',
        'http://ec-iel-localstack:10001/queue/queue-2',
        'http://ec-iel-localstack:10001/queue/queue-3',
        'http://ec-iel-localstack:10001/queue/queue-4'
    ]

    queue = []

    for url in queue_url:
        queue.append(boto3.resource('sqs', **AWS_RESOURCE_CONFIG).Queue(url))

    def fixture(queue_index):
        return queue[queue_index]

    yield fixture
