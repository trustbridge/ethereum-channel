import os
import urllib
import boto3
import pytest
from web3 import Web3
from src.config import Config
from src.contract import Contract

WALLET_PUBLIC_KEY = os.environ['WALLET_PUBLIC_KEY']
WALLET_PRIVATE_KEY = os.environ['WALLET_PRIVATE_KEY']

AWS_ENDPOINT_URL = os.environ['AWS_ENDPOINT_URL']

AWS_RESOURCE_CONFIG = dict(
    endpoint_url=AWS_ENDPOINT_URL,
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
)


@pytest.fixture(scope='function')
def empty_queue():
    client = boto3.client('sqs', **AWS_RESOURCE_CONFIG)

    def get_empty_queue(name):
        queue_url = urllib.parse.urljoin(AWS_ENDPOINT_URL, f'queue/{name}')
        client.purge_queue(QueueUrl=queue_url)
        return boto3.resource('sqs', **AWS_RESOURCE_CONFIG).Queue(queue_url)

    yield get_empty_queue


@pytest.fixture(scope='session')
def emit():
    config = Config.from_file(os.environ['CONFIG_FILE'])
    web3 = Web3(Web3.WebsocketProvider(config.Worker.Blockchain.URI))
    contract = Contract(web3, config.Worker.Contract)

    def emitEvent(name, receiver, text):
        transaction = {
            'from': WALLET_PUBLIC_KEY,
            'nonce': web3.eth.getTransactionCount(WALLET_PUBLIC_KEY, 'pending')
        }
        unsigned_transaction = contract.functions.emitEvent(name, receiver, text).buildTransaction(transaction)
        signed_transaction = web3.eth.account.sign_transaction(
            unsigned_transaction,
            private_key=WALLET_PRIVATE_KEY
        )
        tx_hash = web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
        return web3.eth.waitForTransactionReceipt(tx_hash, 180)
    yield emitEvent


@pytest.fixture(scope='session')
def MessageReceived(emit):
    def Event(receiver, text):
        emit('MessageReceived', receiver, text)
    yield Event


@pytest.fixture(scope='session')
def MessageSent(emit):
    def Event(receiver, text):
        emit('MessageSent', receiver, text)
    yield Event
