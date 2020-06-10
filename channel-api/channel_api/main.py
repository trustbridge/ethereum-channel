from fastapi import FastAPI, Response
from pydantic import BaseModel
from enum import Enum
from web3 import Web3
import json
import os
import boto3
sqs = boto3.client('sqs')

app = FastAPI()

# TODO get from environment
contract_address = os.environ['CONTRACT_ADDRESS']
# '0xDE92b3f2Ca7cc958D5369bd8eAB44CfC70502102'
key = os.environ['PRIVATE_KEY']
# '4EDFAD00D9DF188559D56317896CAF0795ABB70210FA5C8DB62FF35C1A64BB57'

w3 = Web3(Web3.HTTPProvider(
    os.environ['PROVIDER_URL']))
# "https://rinkeby.infura.io/v3/f83e77be0cc14688bc3f8e74576b244a"

account = w3.eth.account.privateKeyToAccount(key)
# w3.eth.defaultAccount = w3.eth.accounts[0]

# TODO: need a better way to get the contract ABI.
# maybe we store in S3 as part of the contract deployment

with open('ChannelNode.json') as f:
    compiled_contract = json.load(f)

ABI = compiled_contract['abi']

contract = w3.eth.contract(contract_address, abi=ABI)


class MessageStatus(str, Enum):
    RECEIVED = "received"
    CONFIRMED = "confirmed"
    REVOKED = "revoked"
    UNDELIVERABLE = "undeliverable"


class MessageRequest(BaseModel):
    sender: str
    receiver: str
    subject: str
    obj: str
    predicate: str


class MessageResponse(BaseModel):
    id: str
    status: MessageStatus
    message: MessageRequest


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/participants")
def get_participants():

    participants = contract.functions.getParticipants().call()
    return participants


@app.get("/messages/{id}", response_model=MessageResponse)
def get_message(id: str) -> MessageResponse:
    txn_receipt = w3.eth.getTransactionReceipt(id)
    txn = w3.eth.getTransaction(id)
    print(txn)
    # status = MessageStatus.UNDELIVERABLE
    current_block = w3.eth.blockNumber
    txn_block = txn['blockNumber']
    confirmation_threshold = 12
    if txn_receipt.status is False:
        status = MessageStatus.UNDELIVERABLE
    elif txn_block is None:
        status = MessageStatus.RECEIVED
    else:
        if current_block - txn_block > confirmation_threshold:
            status = MessageStatus.CONFIRMED
        else:
            status = MessageStatus.RECEIVED
    print(contract.decode_function_input(txn['input']))
    txn_payload = contract.decode_function_input(txn['input'][1]['message'])
    message_payload = MessageRequest(
        subject=txn_payload[1],
        predicate=txn_payload[2],
        obj=txn_payload[3],
        sender=txn_payload[4],
        receiver=txn_payload[5])

    response_message = MessageResponse(
        id=id,
        status=status,
        message=message_payload)

    return response_message


@app.post("/messages", response_model=MessageResponse)
async def create_message(message: MessageRequest, response: Response):
    response.headers["X-Cat-Dog"] = "alone in the world"

    print(contract.address)
    msg = {
        "sender_ref": "1234567890",
        "subject": message.subject,
        "predicate": message.predicate,
        "object": message.obj,
        "sender": message.sender,
        "receiver": message.receiver
    }

    # tx_hash = contract.functions.send(msg).transact()
    txn = contract.functions.send(msg).buildTransaction({
        'gas': 70000,
        'gasPrice': w3.toWei('1', 'gwei'),
        'nonce': w3.eth.getTransactionCount(account.address)
    })
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=key)
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    sqs.send_message(
        QueueUrl=os.environ['QUEUE_URL'], MessageBody=tx_hash.hex())

    message_payload = MessageRequest(
        subject=message.subject,
        predicate=message.predicate,
        obj=message.obj,
        sender=message.sender,
        receiver=message.receiver)

    response_message = MessageResponse(
        id=tx_hash.hex(),
        status=MessageStatus.RECEIVED,
        message=message_payload)

    return response_message
