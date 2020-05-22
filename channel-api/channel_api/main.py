from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
from web3 import Web3
import json

app = FastAPI()

# TODO get from environment
contract_address = '0x6E2312a813f777c83f74a26B15c0f06e76E538d7'
key = '0x64c146fa3b054054519158b614d038ff38497e75dd14ad692cbe562a30932f42'

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.eth.defaultAccount = w3.eth.accounts[0]

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
    return {"bob": id}


@app.post("/messages", response_model=MessageResponse)
async def create_message(message: MessageRequest):
    print(contract.address)
    msg = {
        "sender_ref": "1234567890",
        "subject": message.subject,
        "predicate": message.predicate,
        "object": message.obj,
        "sender": message.sender,
        "receiver": message.receiver
    }

    tx_hash = contract.functions.send(msg).transact()
    message_payload = MessageRequest(
        subject=message.subject,
        predicate=message.predicate,
        obj=message.obj,
        sender=message.sender,
        receiver=message.receiver)

    response_message = MessageResponse(
        id=tx_hash.hex(),
        status=MessageStatus.CONFIRMED,
        message=message_payload)

    return response_message
