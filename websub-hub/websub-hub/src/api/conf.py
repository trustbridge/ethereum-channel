from flask_env import MetaFlaskEnv
from libtrustbridge.utils.conf import env_s3_config


class Config(metaclass=MetaFlaskEnv):

    SERVER_NAME = '0.0.0.0:8080'

    def __init__(self):
        self.SUBSCRIPTIONS_REPO_CONF = env_s3_config('SUBSCRIPTIONS_REPO')
