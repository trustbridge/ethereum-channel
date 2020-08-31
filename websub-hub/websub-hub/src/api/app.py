from flask import Flask
from libtrustbridge.errors import handlers as error_handlers
from src import conf
from src.loggers import logger
from . import views


def create_app(config=None):
    default_config = dict(
        SERVER_NAME=conf.SERVER_NAME,
        SUBSCRIPTIONS_REPO_CONF=conf.SUBSCRIPTIONS_REPO,
        TOPIC_BASE_URL=conf.TOPIC_BASE_URL,
        DEBUG=conf.DEBUG,
        TESTING=conf.TESTING
    )
    config = config or {}
    config = {**default_config, **config}
    app = Flask(__name__)
    app.config.update(config)
    with app.app_context():
        app.logger = logger
        app.register_blueprint(views.blueprint)
        error_handlers.register(app)
    return app
