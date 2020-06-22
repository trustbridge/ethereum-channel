from web3 import Web3
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

sqs = boto3.client('sqs')

# TODO: should be getting this from S3


def get_abi():
    with open('ChannelNode.json') as f:
        compiled_contract = json.load(f)

    ABI = compiled_contract['abi']
    return ABI


def get_client() -> EthereumClient:
    w3 = Web3(Web3.HTTPProvider(
        os.environ['PROVIDER_URL']))
    return w3.eth


def get_w3() -> EthereumClient:
    w3 = Web3(Web3.HTTPProvider(
        os.environ['PROVIDER_URL']))
    return w3


def get_config() -> Config:
    return Config(
        confirmation_threshold=12,
        contract_address=os.environ['CONTRACT_ADDRESS'],
        key=os.environ['PRIVATE_KEY']  # TODO: will need to decrypt
    )


def get_transaction(id: str) -> Transaction:
    w3 = Web3(Web3.HTTPProvider(
        os.environ['PROVIDER_URL']))

    transaction = w3.eth.getTransaction(id)

    return Transaction(**transaction)


def get_transaction_receipt(id: str):
    w3 = Web3(Web3.HTTPProvider(
        os.environ['PROVIDER_URL']))

    transaction_receipt = w3.eth.getTransactionReceipt(id)

    return TransactionReceipt(**transaction_receipt)


def get_contract():
    with open('ChannelNode.json') as f:
        compiled_contract = json.load(f)

    ABI = compiled_contract['abi']

    contract = w3.eth.contract(contract_address, abi=ABI)

    return contract


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


# def transaction_to_message_response(txn: Transaction, txn_receipt: TransactionReceipt) -> MessageResponse:
