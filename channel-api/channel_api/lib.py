from web3 import Web3
from libtrustbridge.utils.conf import string_or_b64kms
from .models import (
    Config,
    EthereumClient,
    MessageRequest,
    MessageResponse,
    MessageStatus,
    Transaction,
    TransactionReceipt)

import boto3
import json
import os

sqs = boto3.resource('sqs', endpoint_url=os.environ.get('AWS_ENDPOINT_URL'))
s3 = boto3.resource('s3', endpoint_url=os.environ.get('AWS_ENDPOINT_URL'))

CONTRACT_BUCKET = os.environ['CONTRACT_BUCKET']
CONTRACT_BUILD_ARTIFACT_KEY = os.environ['CONTRACT_BUILD_ARTIFACT_KEY']
CONTRACT_NETWORK_ID = str(int(os.environ['CONTRACT_NETWORK_ID']))
CONTRACT_OWNER_PRIVATE_KEY = os.environ['CONTRACT_OWNER_PRIVATE_KEY']

HTTP_BLOCKCHAIN_ENDPOINT = os.environ['HTTP_BLOCKCHAIN_ENDPOINT']
SENDER_REF = os.environ['SENDER_REF']


def get_config() -> Config:

    return Config(
        confirmation_threshold=12,
        contract_owner_private_key=string_or_b64kms(CONTRACT_OWNER_PRIVATE_KEY),
        sender_ref=SENDER_REF
    )


def get_w3() -> EthereumClient:
    w3 = Web3(Web3.HTTPProvider(HTTP_BLOCKCHAIN_ENDPOINT))
    return w3


def get_transaction(id: str) -> Transaction:
    w3 = get_w3()

    transaction = w3.eth.getTransaction(id)

    return Transaction(**transaction)


def get_transaction_receipt(id: str):
    w3 = get_w3()

    transaction_receipt = w3.eth.getTransactionReceipt(id)

    return TransactionReceipt(**transaction_receipt)


def transaction_status(
        txn_receipt: TransactionReceipt,
        current_block: int,
        confirmation_threshold: int) -> MessageStatus:
    if txn_receipt.status is False:
        return MessageStatus.UNDELIVERABLE
    elif txn_receipt.blockNumber is None:
        return MessageStatus.RECEIVED
    else:
        if current_block - txn_receipt.blockNumber > confirmation_threshold:
            status = MessageStatus.CONFIRMED
        else:
            status = MessageStatus.RECEIVED
    return status


def get_contract_truffle_build_artifact():
    bucket = s3.Bucket(CONTRACT_BUCKET)
    contract_build_artifact_object = bucket.Object(CONTRACT_BUILD_ARTIFACT_KEY)
    contract_build_artifact = json.load(contract_build_artifact_object.get()['Body'])
    return contract_build_artifact


def get_contract():
    w3 = get_w3()

    contract_build_artifact = get_contract_truffle_build_artifact()
    contract_address = contract_build_artifact['networks'][CONTRACT_NETWORK_ID]['address']
    contract_abi = json.dumps(contract_build_artifact['abi'])
    contract = w3.eth.contract(contract_address, abi=contract_abi)

    return contract
