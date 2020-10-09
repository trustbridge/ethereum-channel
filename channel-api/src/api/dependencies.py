import json
from web3 import Web3
from libtrustbridge.utils.conf import string_or_b64kms
from ..repos import ContractRepo
from .. import config
from .models import Config, EthereumClient


def get_config() -> Config:

    return Config(
        confirmation_threshold=12,
        contract_owner_private_key=string_or_b64kms(config.CONTRACT_OWNER_PRIVATE_KEY),
        sender_ref=config.SENDER_REF,
        sender=config.SENDER
    )


def get_w3() -> EthereumClient:
    return Web3(Web3.HTTPProvider(config.HTTP_BLOCKCHAIN_ENDPOINT))


def get_contract():
    w3 = get_w3()

    contract_build_artifact = json.loads(ContractRepo().get_object_content(config.CONTRACT_BUILD_ARTIFACT_KEY))
    contract_address = contract_build_artifact['networks'][config.CONTRACT_NETWORK_ID]['address']
    contract_abi = json.dumps(contract_build_artifact['abi'])
    contract = w3.eth.contract(contract_address, abi=contract_abi)

    return contract
