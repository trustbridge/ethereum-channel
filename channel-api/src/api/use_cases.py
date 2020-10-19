import uuid
from http import HTTPStatus
import urllib
from box import Box
import requests
from libtrustbridge.websub.domain import Pattern
from libtrustbridge.websub.constants import (
    MODE_ATTR_SUBSCRIBE_VALUE,
    TOPIC_ATTR_KEY,
    MODE_ATTR_KEY,
    LEASE_SECONDS_ATTR_KEY
)
from libtrustbridge.websub.schemas import SubscriptionForm
from libtrustbridge.websub.exceptions import SubscriptionNotFoundError, CallbackURLValidationError
from libtrustbridge.errors.use_case_errors import NotFoundError, BadParametersError, ConflictError, UseCaseError
from marshmallow import Schema, fields, ValidationError as MarshmallowValidationError


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


class GetTopicUseCase:
    def execute(self, topic):
        try:
            Pattern(topic)._validate()
            return topic
        except ValueError as e:
            raise NotFoundError(detail='topic does not exist') from e


class CanonicalURLTopicVerificationUseCase:
    def __init__(self, topic_base_url=None):
        self.topic_base_url = topic_base_url if topic_base_url.endswith('/') else f'{topic_base_url}/'

    def execute(self, topic: str = None, topic_prefix: str = None):
        parsed_topic_url = urllib.parse.urlparse(topic)
        if parsed_topic_url.scheme:
            topic_canonical_url = topic
            if topic_canonical_url.startswith(self.topic_base_url):
                topic = topic[len(self.topic_base_url):]
                if topic_prefix:
                    topic = f'{topic_prefix}.{topic}'
                    topic_canonical_url = urllib.parse.urljoin(self.topic_base_url, topic)
                try:
                    Pattern(topic)._validate()
                except ValueError as e:
                    raise BadParametersError(detail=f'"{topic}" is invalid topic string') from e
            else:
                raise BadParametersError(
                    detail=f'Topic url "{topic_canonical_url}" must start with "{self.topic_base_url}"'
                )

            response = requests.get(topic_canonical_url)
            if response.status_code == HTTPStatus.OK:
                topic_response = response.json()
                if topic_response == topic:
                    return topic
                else:
                    raise ConflictError(
                        detail='Unexpected topic string returned by the channel, expected: "{}", got:"{}"'.format(
                            topic, topic_response
                        )
                    )
            elif response.status_code == HTTPStatus.NOT_FOUND:
                raise NotFoundError(detail=f'Topic "{topic}" does not exist')
            elif response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR:
                raise UseCaseError(generic_http_error=True, status=response.status_code, )
        else:
            if topic_prefix:
                topic = f'{topic_prefix}.{topic}'
            return topic


class SubscriptionCallbackVerificationUseCase:
    def execute(self, callback: str = None, mode: str = None, topic: str = None, lease_seconds: str = None):
        challenge = str(uuid.uuid4())
        params = {
            MODE_ATTR_KEY: mode,
            TOPIC_ATTR_KEY: topic,
            LEASE_SECONDS_ATTR_KEY: lease_seconds,
            'hub.challenge': challenge
        }
        try:
            response = requests.get(callback, params)
            if response.status_code == HTTPStatus.OK and response.text == challenge:
                return
            raise CallbackURLValidationError()
        except requests.exceptions.RequestException as e:
            raise CallbackURLValidationError() from e


class SubscribeUseCase:
    def __init__(self, subscriptions_repo=None):
        self.subscriptions_repo = subscriptions_repo

    def execute(self, callback=None, topic=None, expiration=None):
        self.subscriptions_repo.subscribe_by_pattern(Pattern(topic), callback, expiration)


class UnsubscribeUseCase:
    def __init__(self, subscriptions_repo=None):
        self.subscriptions_repo = subscriptions_repo

    def execute(self, callback: str = None, topic: str = None):
        pattern = Pattern(topic)
        subscriptions = self.subscriptions_repo.get_subscriptions_by_pattern(pattern)
        subscriptions_by_callbacks = [s for s in subscriptions if s.callback_url == callback]
        if not subscriptions_by_callbacks:
            raise SubscriptionNotFoundError()
        self.subscriptions_repo.bulk_delete([pattern.to_key(callback)])


class SubscriptionActionUseCase:
    def __init__(self, subscriptions_repo=None, topic_base_url: str = None):
        self.subscribe = SubscribeUseCase(subscriptions_repo)
        self.unsubscribe = UnsubscribeUseCase(subscriptions_repo)
        self.subscription_callback_verification = SubscriptionCallbackVerificationUseCase()
        self.canonical_url_topic_verification = CanonicalURLTopicVerificationUseCase(topic_base_url)

    def execute(self, websub_form_data: dict = None, topic_prefix: str = None):
        try:
            data = Box(SubscriptionForm().load(websub_form_data))
        except MarshmallowValidationError as e:
            raise BadParametersError(detail=str(e)) from e
        data.topic = self.canonical_url_topic_verification.execute(data.topic, topic_prefix)
        if data.mode == MODE_ATTR_SUBSCRIBE_VALUE:
            self.subscription_callback_verification.execute(
                callback=data.callback,
                topic=data.topic,
                mode=data.mode,
                lease_seconds=data.lease_seconds
            )
            self.subscribe.execute(
                callback=data.callback,
                topic=data.topic,
                expiration=data.lease_seconds
            )
        else:
            self.unsubscribe.execute(callback=data.callback, topic=data.topic)
