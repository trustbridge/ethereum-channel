import urllib
from box import Box
from flask import Flask
from web3 import Web3
from web3.gas_strategies import time_based as gas_price_strategies
from libtrustbridge.errors import handlers as error_handlers
from src import repos
from . import views as api
from .contract import Contract


def create_app(config: Box = None):
    app = Flask(__name__)
    app.config = Box(app.config)
    app.config.update(config)
    with app.app_context():

        app.web3 = Web3(Web3.HTTPProvider(config.HTTP_BLOCKCHAIN_ENDPOINT))

        if config.BLOCKCHAIN_GAS_PRICE_STRATEGY == 'fast':
            app.web3.eth.setGasPriceStrategy(gas_price_strategies.fast_gas_price_strategy)
        elif config.BLOCKCHAIN_GAS_PRICE_STRATEGY == 'medium':
            app.web3.eth.setGasPriceStrategy(gas_price_strategies.medium_gas_price_strategy)
        else:
            raise ValueError(
                'BLOCKCHAIN_GAS_PRICE must be in ["fast", "medium"], got: "{}"'.format(
                    config.BLOCKCHAIN_GAS_PRICE_STRATEGY
                )
            )

        app.repos = Box(
            subscriptions=repos.Subscriptions(config=config.SUBSCRIPTIONS_REPO),
            contract=repos.Contract(config=config.CONTRACT_REPO)
        )
        app.contract = Contract(
            web3=app.web3,
            repo=app.repos.contract,
            network_id=config.CONTRACT_NETWORK_ID,
            artifact_key=config.CONTRACT_BUILD_ARTIFACT_KEY
        )

        app.register_blueprint(api.blueprint)
        error_handlers.register(app)

        app.config.TOPIC_BASE_URL = urllib.parse.urljoin(config.CHANNEL_URL, api.TOPIC_BASE_URL)

    return app
