from .lib import (
    get_config,
    get_contract,
    get_w3,
    transaction_status
)
from .models import (
    Config,
    EthereumClient,
    MessageRequest,
    MessageResponse,
    MessageStatus,
    Transaction,
    TransactionReceipt)
from fastapi import Depends, FastAPI, Response, HTTPException, status
from libtrustbridge.websub.domain import Pattern
import json


app = FastAPI()


@app.get('/topic/{topic}', status_code=status.HTTP_200_OK)
def get_topic(topic):
    try:
        Pattern(topic)._validate()
        return topic
    except ValueError:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.get("/participants")
def get_participants(contract: object = Depends(get_contract)):

    participants = contract.functions.getParticipants().call()
    return participants


@app.get("/messages/{id}", response_model=MessageResponse)
def get_message(id: str,
                w3: EthereumClient = Depends(get_w3),
                config: Config = Depends(get_config),
                contract: object = Depends(get_contract)
                ) -> MessageResponse:
    txn = w3.eth.getTransaction(id)
    txn_receipt = w3.eth.getTransactionReceipt(id)
    current_block = w3.eth.blockNumber
    status = transaction_status(txn_receipt, current_block, config.confirmation_threshold)
    txn_payload = contract.decode_function_input(txn.input)[1]['message']

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
async def create_message(message: MessageRequest,
                         response: Response,
                         w3: EthereumClient = Depends(get_w3),
                         config: Config = Depends(get_config),
                         contract: object = Depends(get_contract)):

    msg = {
        "subject": message.subject,
        "predicate": message.predicate,
        "object": message.obj,
        "sender": message.sender,
        "receiver": message.receiver,
        "sender_ref": config.sender_ref
    }

    account = w3.eth.account.privateKeyToAccount(config.contract_owner_private_key)
    nonce = w3.eth.getTransactionCount(account.address)

    # gas price and gas amount should be determined automatically using ethereum node API
    txn = contract.functions.send(msg).buildTransaction({
        'nonce': nonce
    })
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=config.contract_owner_private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    # sqs.send_message(
    #     QueueUrl=os.environ['OUTBOUND_MESSAGE_QUEUE_URL'], MessageBody=tx_hash.hex())

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
