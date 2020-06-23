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
import base64
import logging

sqs = boto3.client('sqs')

BASE64_PREFIX_1 = 'base64:'
BASE64_PREFIX_2 = 'kms+base64:'
AWS_REGION = os.environ.get('AWS_REGION', None)


def decrypt_kms_data(encrypted_data):
    """Decrypt KMS encoded data."""
    import boto3  # local import so we don't need it installed for demo and local
    if not AWS_REGION:
        logging.error(
            "Trying to decrypt KMS value but no AWS region set"
        )
        return None

    kms = boto3.client('kms', region_name=AWS_REGION)
    decrypted = kms.decrypt(CiphertextBlob=encrypted_data)

    if decrypted.get('KeyId'):
        # Decryption succeed
        decrypted_value = decrypted.get('Plaintext', '')
        if isinstance(decrypted_value, bytes):
            decrypted_value = decrypted_value.decode('utf-8')
        return decrypted_value


def string_or_b64kms(value):
    """Check if value is base64 encoded - if yes, decode it using KMS."""

    if not value:
        return value

    try:
        # Check if environment value base64 encoded
        if isinstance(value, (str, bytes)):
            encrypted_value = None
            if value.startswith(BASE64_PREFIX_1):
                encrypted_value = value[len(BASE64_PREFIX_1):]
            elif value.startswith(BASE64_PREFIX_2):
                encrypted_value = value[len(BASE64_PREFIX_2):]
            else:
                # non-encrypted value
                return value
            # If yes, decode it using AWS KMS
            data = base64.b64decode(encrypted_value)
            decrypted_value = decrypt_kms_data(data)

            # If decryption succeed, use it
            if decrypted_value:
                value = decrypted_value
    except Exception as e:
        logging.exception(e)
    return value


def get_client() -> EthereumClient:
    w3 = Web3(Web3.HTTPProvider(
        os.environ['RPC_URL']))
    return w3.eth


def get_w3() -> EthereumClient:
    w3 = Web3(Web3.HTTPProvider(
        os.environ['RPC_URL']))
    return w3


def get_config() -> Config:

    return Config(
        confirmation_threshold=12,
        contract_address=os.environ['CONTRACT_ADDRESS'],
        key=string_or_b64kms(os.environ['PRIVATE_KEY'])  # TODO: will need to decrypt
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


# TODO: once abi being stored in s3 then this needs to be
# changed to pull from there instead
def get_abi():
    abi_string = '[{"inputs": [{"internalType": "string[]", "name": "_participantList", "type": "string[]"}], "payable": false, "stateMutability": "nonpayable", "type": "constructor"}, {"anonymous": false, "inputs": [{"components": [{"internalType": "string", "name": "sender_ref", "type": "string"}, {"internalType": "string", "name": "subject", "type": "string"}, {"internalType": "string", "name": "predicate", "type": "string"}, {"internalType": "string", "name": "object", "type": "string"}, {"internalType": "string", "name": "sender", "type": "string"}, {"internalType": "string", "name": "receiver", "type": "string"}], "indexed": false, "internalType": "struct ChannelNode.Message", "name": "message", "type": "tuple"}], "name": "MessageReceivedEvent", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "internalType": "string", "name": "sender_ref", "type": "string"}], "name": "MessageSentEvent", "type": "event"}, {"constant": true, "inputs": [], "name": "owner", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": true, "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "name": "participantList", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": true, "inputs": [{"internalType": "string", "name": "", "type": "string"}], "name": "participants", "outputs": [{"internalType": "address", "name": "participantAddress", "type": "address"}, {"internalType": "contract ChannelNode", "name": "participantContract", "type": "address"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": true, "inputs": [], "name": "getParticipants", "outputs": [{"internalType": "string[]", "name": "", "type": "string[]"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": true, "inputs": [{"internalType": "string", "name": "participant", "type": "string"}], "name": "getParticipant", "outputs": [{"components": [{"internalType": "address", "name": "participantAddress", "type": "address"}, {"internalType": "contract ChannelNode", "name": "participantContract", "type": "address"}], "internalType": "struct ChannelNode.Participant", "name": "", "type": "tuple"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": false, "inputs": [{"internalType": "string", "name": "_name", "type": "string"}, {"internalType": "address", "name": "_address", "type": "address"}], "name": "addParticipant", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": false, "inputs": [{"internalType": "string", "name": "_name", "type": "string"}, {"internalType": "address", "name": "_address", "type": "address"}], "name": "updateParticipantContractAddress", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": false, "inputs": [{"components": [{"internalType": "string", "name": "sender_ref", "type": "string"}, {"internalType": "string", "name": "subject", "type": "string"}, {"internalType": "string", "name": "predicate", "type": "string"}, {"internalType": "string", "name": "object", "type": "string"}, {"internalType": "string", "name": "sender", "type": "string"}, {"internalType": "string", "name": "receiver", "type": "string"}], "internalType": "struct ChannelNode.Message", "name": "message", "type": "tuple"}], "name": "receiveMessage", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": false, "inputs": [{"components": [{"internalType": "string", "name": "sender_ref", "type": "string"}, {"internalType": "string", "name": "subject", "type": "string"}, {"internalType": "string", "name": "predicate", "type": "string"}, {"internalType": "string", "name": "object", "type": "string"}, {"internalType": "string", "name": "sender", "type": "string"}, {"internalType": "string", "name": "receiver", "type": "string"}], "internalType": "struct ChannelNode.Message", "name": "message", "type": "tuple"}], "name": "send", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}]'
    abi = json.loads(abi_string)
    return abi


def get_contract():
    w3 = get_w3()
    ABI = get_abi()

    contract = w3.eth.contract(contract_address, abi=ABI)

    return contract
