from flask_env import MetaFlaskEnv
from libtrustbridge.utils.conf import env_s3_config


class Config(metaclass=MetaFlaskEnv):

    DEBUG = False
    SERVICE_NAME = 'ethereum-channel-websub-hub'
    SERVER_NAME = '0.0.0.0:8080'
    ENDPOINT = 'AU'

    def __init__(self):
        self.SUBSCRIPTIONS_REPO_CONF = env_s3_config('SUBSCRIPTIONS_REPO')
