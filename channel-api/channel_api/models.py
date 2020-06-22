from pydantic import BaseModel
from enum import Enum
from typing import Any, Callable, List, Optional


class Config(BaseModel):
    confirmation_threshold: int
    contract_address: str
    key: str


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


class Transaction(BaseModel):
    blockHash: Any
    blockNumber: int
    from_: str
    gas: int
    gasPrice: int
    hash: Any
    input: str
    nonce: int
    r: Any
    s: Any
    to: str
    transactionIndex: int
    v: int
    value: int

    class Config:
        fields = {
            'from_': 'from'
        }


class TransactionReceiptLog(BaseModel):
    address: str
    blockHash: Any
    blockNumber: int
    data: str
    logIndex: int
    removed: bool
    topics: List[Any]
    transactionHash: Any
    transactionIndex: int


class TransactionReceipt(BaseModel):
    blockHash: Any
    blockNumber: int
    contractAddress: Optional[str]
    cumulativeGasUsed: int
    from_: str
    gasUsed: int
    logs: List[TransactionReceiptLog]
    logsBloom: Any
    status: int
    to: str
    transactionHash: Any
    transactionIndex: int

    class Config:
        fields = {
            'from_': 'from'
        }


class EthereumClient(BaseModel):
    getTransaction: Callable[[str], Transaction]
    getTransactionReceipt: Callable[[str], TransactionReceipt]
    blockNumber: int
