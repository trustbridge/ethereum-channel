from .models import (
    MessageStatus,
    TransactionReceipt
)


def transaction_status(
    txn_receipt: TransactionReceipt,
    current_block: int,
    confirmation_threshold: int
) -> MessageStatus:
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
