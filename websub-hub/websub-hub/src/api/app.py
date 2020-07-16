from flask import Flask, url_for
from libtrustbridge.errors import handlers as error_handlers
from src.loggers import logger
from . import views
from . import conf


def create_app(config=None):
    config = config or conf.Config()
    app = Flask(__name__)
    app.config.from_object(config)
    with app.app_context():
        app.logger = logger
        app.register_blueprint(views.blueprint)
        error_handlers.register(app)
        app.config['HUB_URL'] = url_for('api.subscriptions_by_id')
    return app
