from flask import Flask, url_for
from src.loggers import logging
from . import conf


def create_app(config=None):
    config = config or conf.Config()
    app = Flask(__name__)
    app.config.from_object(config)
    app.logger = logging.getLogger(app.config['SERVICE_NAME'])
    with app.app_context():
        from . import views
        app.register_blueprint(views.blueprint)
        app.config['HUB_URL'] = url_for('api.subscriptions_by_id')
    return app
