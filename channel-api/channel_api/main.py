from .lib import (
    get_abi,
    get_client,
    get_config,
    get_contract,
    get_w3
)
from .models import (
    Config,
    EthereumClient,
    MessageRequest,
    MessageResponse,
    MessageStatus,
    Transaction,
    TransactionReceipt)
from fastapi import Depends, FastAPI, Response
import json


app = FastAPI()


# TODO: need a better way to get the contract ABI.
# maybe we store in S3 as part of the contract deployment


@app.get("/participants")
def get_participants(contract: object = Depends(get_contract)):

    participants = contract.functions.getParticipants().call()
    return participants


@app.get("/messages/{id}", response_model=MessageResponse)
def get_message(id: str,
                client: EthereumClient = Depends(get_client),
                config: Config = Depends(get_config),
                contract_abi: dict = Depends(get_abi)) -> MessageResponse:
    txn = client.getTransaction(id)
    txn_receipt = client.getTransactionReceipt(id)

    contract = client.contract(config.contract_address, abi=contract_abi)

    current_block = client.blockNumber
    txn_block = txn.blockNumber

    if txn_receipt.status is False:
        status = MessageStatus.UNDELIVERABLE
    elif txn_block is None:
        status = MessageStatus.RECEIVED
    else:
        if current_block - txn_block > config.confirmation_threshold:
            status = MessageStatus.CONFIRMED
        else:
            status = MessageStatus.RECEIVED

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
                         client: EthereumClient = Depends(get_client),
                         w3: EthereumClient = Depends(get_w3),
                         config: Config = Depends(get_config),
                         contract_abi: dict = Depends(get_abi)):

    contract = client.contract(config.contract_address, abi=contract_abi)

    msg = {
        "subject": message.subject,
        "predicate": message.predicate,
        "object": message.obj,
        "sender": message.sender,
        "receiver": message.receiver
    }

    account = client.account.privateKeyToAccount(config.key)
    nonce = client.getTransactionCount(account.address)

    # tx_hash = contract.functions.send(msg).transact()
    txn = contract.functions.send(msg).buildTransaction({
        'gas': 70000,
        'gasPrice': w3.toWei('1', 'gwei'),
        'nonce': nonce  # client.getTransactionCount(account.address)
    })
    signed_txn = client.account.sign_transaction(
        txn, private_key=config.key)
    tx_hash = client.sendRawTransaction(signed_txn.rawTransaction)
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
