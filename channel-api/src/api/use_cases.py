from marshmallow import Schema, fields


class SendMessageUseCase:
    class MessageStatus:
        RECEIVED = "received"
        CONFIRMED = "confirmed"
        REVOKED = "revoked"
        UNDELIVERABLE = "undeliverable"

    class MessageSchema(Schema):
        subject = fields.String(required=True)
        predicate = fields.String(required=True)
        object = fields.String(required=True)
        receiver = fields.String(required=True)

    def __init__(self, web3, contract, contract_owner_private_key):
        self.web3 = web3
        self.contract = contract
        self.contract_owner_private_key = contract_owner_private_key

    def execute(self, message, sender, sender_ref):
        # validating message structure
        self.MessageSchema().load(message)
        message = {**message, 'sender': sender, 'sender_ref': sender_ref}

        account = self.web3.eth.account.privateKeyToAccount(self.contract_owner_private_key)
        nonce = self.web3.eth.getTransactionCount(account.address)

        # gas price and gas amount should be determined automatically using ethereum node API
        txn = self.contract.functions.send(message).buildTransaction({'nonce': nonce})
        signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=self.contract_owner_private_key)
        tx_hash = self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return dict(
            id=tx_hash.hex(),
            status=self.MessageStatus.RECEIVED,
            message=message
        )


class GetMessageUseCase:
    def __init__(self, web3, contract, confirmation_threshold):
        self.web3 = web3
        self.contract = contract
        self.confirmation_threshold = confirmation_threshold

    def execute(self, id):
        tx = self.web3.eth.getTransaction(id)
        tx_receipt = self.web3.eth.getTransactionReceipt(id)
        current_block = self.web3.eth.blockNumber
        if tx_receipt.status is False:
            status = SendMessageUseCase.MessageStatus.UNDELIVERABLE
        elif tx_receipt.blockNumber is None:
            status = SendMessageUseCase.MessageStatus.RECEIVED
        else:
            if current_block - tx_receipt.blockNumber > self.confirmation_threshold:
                status = SendMessageUseCase.MessageStatus.CONFIRMED
            else:
                status = SendMessageUseCase.MessageStatus.RECEIVED
        tx_payload = self.contract.decode_function_input(tx.input)[1]['message']
        message = dict(
            sender_ref=tx_payload[0],
            subject=tx_payload[1],
            predicate=tx_payload[2],
            object=tx_payload[3],
            sender=tx_payload[4],
            receiver=tx_payload[5]
        )
        return dict(
            id=id,
            status=status,
            message=message
        )


class GetParticipantsUseCase:
    def __init__(self, contract):
        self.contract = contract

    def execute(self):
        return self.contract.functions.getParticipants().call()
