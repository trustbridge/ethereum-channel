import json

from .config import Config
from . import repos


def Contract(web3):
    config = Config()
    artifact = json.loads(repos.Contract().get_object_content(config.CONTRACT_BUILD_ARTIFACT_KEY))
    return web3.eth.contract(address=artifact['networks'][config.CONTRACT_NETWORK_ID]['address'], abi=artifact['abi'])
