from web3 import Web3
from box import Box
from src import repos
from src.contract import Contract
from src.processors import SelfIteratingProcessor
from . import use_cases


def MessageSender(config: Box = None):
    web3 = Web3(Web3.HTTPProvider(config.HTTP_BLOCKCHAIN_ENDPOINT))
    contract_repo = repos.Contract(config.CONTRACT_REPO)
    messages_repo = repos.Messages(config.MESSAGES_REPO)
    contract = Contract(
        web3=web3,
        repo=contract_repo,
        network_id=config.CONTRACT_NETWORK_ID,
        artifact_key=config.CONTRACT_BUILD_ARTIFACT_KEY
    )
    use_case = use_cases.ProcessMessageQueueUseCase(
        web3=web3,
        contract=contract,
        sender_private_key=config.SENDER_ACCOUNT_PRIVATE_KEY,
        gas_price_strategy=config.BLOCKCHAIN_GAS_PRICE_STRATEGY,
        gas_price_refresh_rate=config.BLOCKCHAIN_GAS_PRICE_REFRESH_RATE,
        gas_price_increase_factor=config.BLOCKCHAIN_GAS_PRICE_INCREASE_FACTOR,
        messages_repo=messages_repo
    )
    return SelfIteratingProcessor(use_case=use_case)
