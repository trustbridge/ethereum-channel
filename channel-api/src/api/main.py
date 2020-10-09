from . import utils
from . import dependencies as deps
from .models import (
    Config,
    EthereumClient,
    MessageRequest,
    MessageResponse,
    MessageStatus,
)
from fastapi import Depends, FastAPI, Response, HTTPException, status
from libtrustbridge.websub.domain import Pattern


app = FastAPI()


# websub methods
@app.get('/topic/{topic}', status_code=status.HTTP_200_OK)
def get_topic(topic):
    try:
        Pattern(topic)._validate()
        return topic
    except ValueError:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.post('/messages/subscriptions/by_id')
def subscriptions_by_id():
    pass


@app.post('/messages/subscriptions/by_jurisdiction')
def subscriptions_by_jurisdiction():
    pass


# channel api methods
@app.get("/participants")
def get_participants(contract: object = Depends(deps.get_contract)):
    participants = contract.functions.getParticipants().call()
    return participants


@app.get("/messages/{id}", response_model=MessageResponse)
def get_message(
    id: str,
    w3: EthereumClient = Depends(deps.get_w3),
    config: Config = Depends(deps.get_config),
    contract: object = Depends(deps.get_contract)
) -> MessageResponse:
    txn = w3.eth.getTransaction(id)
    txn_receipt = w3.eth.getTransactionReceipt(id)
    current_block = w3.eth.blockNumber
    status = utils.transaction_status(txn_receipt, current_block, config.confirmation_threshold)
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
async def create_message(
    message: MessageRequest,
    response: Response,
    w3: EthereumClient = Depends(deps.get_w3),
    config: Config = Depends(deps.get_config),
    contract: object = Depends(deps.get_contract)
) -> MessageResponse:

    msg = {
        "subject": message.subject,
        "predicate": message.predicate,
        "object": message.obj,
        "receiver": message.receiver,
        "sender": config.sender,
        "sender_ref": config.sender_ref
    }

    account = w3.eth.account.privateKeyToAccount(config.contract_owner_private_key)
    nonce = w3.eth.getTransactionCount(account.address)

    # gas price and gas amount should be determined automatically using ethereum node API
    txn = contract.functions.send(msg).buildTransaction({'nonce': nonce})
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=config.contract_owner_private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    message_payload = MessageRequest(
        subject=message.subject,
        predicate=message.predicate,
        obj=message.obj,
        sender=message.sender,
        receiver=message.receiver
    )

    response_message = MessageResponse(
        id=tx_hash.hex(),
        status=MessageStatus.RECEIVED,
        message=message_payload
    )

    return response_message
