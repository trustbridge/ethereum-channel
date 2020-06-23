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
    contract_string = "  \"abi\": [\n    {\n      \"inputs\": [\n        {\n          \"internalType\": \"string[]\",\n          \"name\": \"_participantList\",\n          \"type\": \"string[]\"\n        }\n      ],\n      \"stateMutability\": \"nonpayable\",\n      \"type\": \"constructor\"\n    },\n    {\n      \"anonymous\": false,\n      \"inputs\": [\n        {\n          \"components\": [\n            {\n              \"internalType\": \"string\",\n              \"name\": \"subject\",\n              \"type\": \"string\"\n            },\n            {\n              \"internalType\": \"string\",\n              \"name\": \"predicate\",\n              \"type\": \"string\"\n            },\n            {\n              \"internalType\": \"string\",\n              \"name\": \"object\",\n              \"type\": \"string\"\n            },\n            {\n              \"internalType\": \"string\",\n              \"name\": \"sender\",\n              \"type\": \"string\"\n            },\n            {\n              \"internalType\": \"string\",\n              \"name\": \"receiver\",\n              \"type\": \"string\"\n            }\n          ],\n          \"indexed\": false,\n          \"internalType\": \"struct ChannelNode.Message\",\n          \"name\": \"message\",\n          \"type\": \"tuple\"\n        }\n      ],\n      \"name\": \"MessageReceivedEvent\",\n      \"type\": \"event\"\n    },\n    {\n      \"anonymous\": false,\n      \"inputs\": [\n        {\n          \"indexed\": false,\n          \"internalType\": \"string\",\n          \"name\": \"subject\",\n          \"type\": \"string\"\n        }\n      ],\n      \"name\": \"MessageSentEvent\",\n      \"type\": \"event\"\n    },\n    {\n      \"inputs\": [],\n      \"name\": \"owner\",\n      \"outputs\": [\n        {\n          \"internalType\": \"address\",\n          \"name\": \"\",\n          \"type\": \"address\"\n        }\n      ],\n      \"stateMutability\": \"view\",\n      \"type\": \"function\",\n      \"constant\": true\n    },\n    {\n      \"inputs\": [\n        {\n          \"internalType\": \"uint256\",\n          \"name\": \"\",\n          \"type\": \"uint256\"\n        }\n      ],\n      \"name\": \"participantList\",\n      \"outputs\": [\n        {\n          \"internalType\": \"string\",\n          \"name\": \"\",\n          \"type\": \"string\"\n        }\n      ],\n      \"stateMutability\": \"view\",\n      \"type\": \"function\",\n      \"constant\": true\n    },\n    {\n      \"inputs\": [\n        {\n          \"internalType\": \"string\",\n          \"name\": \"\",\n          \"type\": \"string\"\n        }\n      ],\n      \"name\": \"participants\",\n      \"outputs\": [\n        {\n          \"internalType\": \"address\",\n          \"name\": \"participantAddress\",\n          \"type\": \"address\"\n        },\n        {\n          \"internalType\": \"contract ChannelNode\",\n          \"name\": \"participantContract\",\n          \"type\": \"address\"\n        }\n      ],\n      \"stateMutability\": \"view\",\n      \"type\": \"function\",\n      \"constant\": true\n    },\n    {\n      \"inputs\": [],\n      \"name\": \"getParticipants\",\n      \"outputs\": [\n        {\n          \"internalType\": \"string[]\",\n          \"name\": \"\",\n          \"type\": \"string[]\"\n        }\n      ],\n      \"stateMutability\": \"view\",\n      \"type\": \"function\",\n      \"constant\": true\n    },\n    {\n      \"inputs\": [\n        {\n          \"internalType\": \"string\",\n          \"name\": \"participant\",\n          \"type\": \"string\"\n        }\n      ],\n      \"name\": \"getParticipant\",\n      \"outputs\": [\n        {\n          \"components\": [\n            {\n              \"internalType\": \"address\",\n              \"name\": \"participantAddress\",\n              \"type\": \"address\"\n            },\n            {\n              \"internalType\": \"contract ChannelNode\",\n              \"name\": \"participantContract\",\n              \"type\": \"address\"\n            }\n          ],\n          \"internalType\": \"struct ChannelNode.Participant\",\n          \"name\": \"\",\n          \"type\": \"tuple\"\n        }\n      ],\n      \"stateMutability\": \"view\",\n      \"type\": \"function\",\n      \"constant\": true\n    },\n    {\n      \"inputs\": [\n        {\n          \"internalType\": \"string\",\n          \"name\": \"_name\",\n          \"type\": \"string\"\n        },\n        {\n          \"internalType\": \"address\",\n          \"name\": \"_address\",\n          \"type\": \"address\"\n        }\n      ],\n      \"name\": \"addParticipant\",\n      \"outputs\": [],\n      \"stateMutability\": \"nonpayable\",\n      \"type\": \"function\"\n    },\n    {\n      \"inputs\": [\n        {\n          \"internalType\": \"string\",\n          \"name\": \"_name\",\n          \"type\": \"string\"\n        },\n        {\n          \"internalType\": \"address\",\n          \"name\": \"_address\",\n          \"type\": \"address\"\n        }\n      ],\n      \"name\": \"updateParticipantContractAddress\",\n      \"outputs\": [],\n      \"stateMutability\": \"nonpayable\",\n      \"type\": \"function\"\n    },\n    {\n      \"inputs\": [\n        {\n          \"components\": [\n            {\n              \"internalType\": \"string\",\n              \"name\": \"subject\",\n              \"type\": \"string\"\n            },\n            {\n              \"internalType\": \"string\",\n              \"name\": \"predicate\",\n              \"type\": \"string\"\n            },\n            {\n              \"internalType\": \"string\",\n              \"name\": \"object\",\n              \"type\": \"string\"\n            },\n            {\n              \"internalType\": \"string\",\n              \"name\": \"sender\",\n              \"type\": \"string\"\n            },\n            {\n              \"internalType\": \"string\",\n              \"name\": \"receiver\",\n              \"type\": \"string\"\n            }\n          ],\n          \"internalType\": \"struct ChannelNode.Message\",\n          \"name\": \"message\",\n          \"type\": \"tuple\"\n        }\n      ],\n      \"name\": \"receiveMessage\",\n      \"outputs\": [],\n      \"stateMutability\": \"nonpayable\",\n      \"type\": \"function\"\n    },\n    {\n      \"inputs\": [\n        {\n          \"components\": [\n            {\n              \"internalType\": \"string\",\n              \"name\": \"subject\",\n              \"type\": \"string\"\n            },\n            {\n              \"internalType\": \"string\",\n              \"name\": \"predicate\",\n              \"type\": \"string\"\n            },\n            {\n              \"internalType\": \"string\",\n              \"name\": \"object\",\n              \"type\": \"string\"\n            },\n            {\n              \"internalType\": \"string\",\n              \"name\": \"sender\",\n              \"type\": \"string\"\n            },\n            {\n              \"internalType\": \"string\",\n              \"name\": \"receiver\",\n              \"type\": \"string\"\n            }\n          ],\n          \"internalType\": \"struct ChannelNode.Message\",\n          \"name\": \"message\",\n          \"type\": \"tuple\"\n        }\n      ],\n      \"name\": \"send\",\n      \"outputs\": [],\n      \"stateMutability\": \"nonpayable\",\n      \"type\": \"function\"\n    }\n  ]"
    compiled_contract = json.loads(contract_string)
    return compiled_contract['abi']
# def transaction_to_message_response(txn: Transaction, txn_receipt: TransactionReceipt) -> MessageResponse:


def get_contract():
    w3 = get_w3()
    ABI = get_abi()

    contract = w3.eth.contract(contract_address, abi=ABI)

    return contract
