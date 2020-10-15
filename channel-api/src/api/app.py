from flask import Flask
from web3 import Web3
from libtrustbridge.errors import handlers as error_handlers
from .config import Config
from .views import blueprint as api
from .contract import Contract


def create_app():
    config = Config()
    app = Flask(__name__)
    app.config.update(dict(
        # SERVER_NAME=config.SERVER_NAME,
        CONTRACT_OWNER_PRIVATE_KEY=config.CONTRACT_OWNER_PRIVATE_KEY,
        MESSAGE_CONFIRMATION_THRESHOLD=config.MESSAGE_CONFIRMATION_THRESHOLD,
        SENDER=config.SENDER,
        SENDER_REF=config.SENDER_REF,
        DEBUG=config.DEBUG,
        TESTING=config.TESTING,
    ))

    with app.app_context():

        app.web3 = Web3(Web3.HTTPProvider(config.HTTP_BLOCKCHAIN_ENDPOINT))
        app.contract = Contract(app.web3)

        app.register_blueprint(api)
        error_handlers.register(app)

    return app
