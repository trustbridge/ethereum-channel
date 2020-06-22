import os
import json
import yaml
import boto3
import pytest
from web3 import Web3

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

    def clean_queues():
        client = boto3.client('sqs', **AWS_RESOURCE_CONFIG)
        for url in queue_url:
            client.purge_queue(QueueUrl=url)

    clean_queues()

    queues = []

    for url in queue_url:
        queues.append(boto3.resource('sqs', **AWS_RESOURCE_CONFIG).Queue(url))

    def queue_getter(queue_index):
        return queues[queue_index]

    yield queue_getter

    clean_queues()


@pytest.fixture(scope='session')
def emitEvent():
    with open(os.environ['CONFIG_FILE'], 'rt') as f:
        config = yaml.safe_load(f)
        contract = config['Worker']['Contract']
        blockchain_uri = config['Worker']['Blockchain']['URI']
        with open(contract['ABI'], 'rt') as f:
            abi = json.load(f)['abi']
        with open(contract['Address'], 'rt') as f:
            address = f.read()

    web3 = Web3(Web3.WebsocketProvider(blockchain_uri))
    contract = web3.eth.contract(address, abi=abi)
    transaction = {
        'from': os.environ['TEST_ETH_ACCOUNT']
    }

    def emitEvent(eventIndex, message):
        tx_hash = contract.functions.emitEvent(eventIndex, message).transact(transaction)
        return web3.eth.waitForTransactionReceipt(tx_hash, 180)
    yield emitEvent


@pytest.fixture(scope='session')
def get_sqs_msgs(queue):
    def get_sqs_msgs(queue_index, wait_time_seconds=1, max_number_of_messages=1):
        messages = queue(queue_index).receive_messages(
            WaitTimeSeconds=wait_time_seconds,
            MaxNumberOfMessages=max_number_of_messages
        )
        return messages
    yield get_sqs_msgs
