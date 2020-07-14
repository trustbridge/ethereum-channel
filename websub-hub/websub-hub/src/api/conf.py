from os import environ
from flask_env import MetaFlaskEnv


class Config(metaclass=MetaFlaskEnv):
    DEBUG = False
    SERVICE_NAME = 'ethereum-channel-websub-hub'
    SERVER_NAME = '0.0.0.0:8080'
    ENDPOINT = 'AU'
    LOG_FORMATTER_JSON = False
    SENTRY_DSN = environ.get('SENTRY_DSN')
