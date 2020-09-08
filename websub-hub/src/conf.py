from libtrustbridge.utils.conf import env_s3_config, env_queue_config, env, env_bool


def env_base_url(key):
    value = env(key)
    return value if value.endswith('/') else value + '/'


NOTIFICATIONS_REPO = env_queue_config('NOTIFICATIONS_REPO')
DELIVERY_OUTBOX_REPO = env_queue_config('DELIVERY_OUTBOX_REPO')
SUBSCRIPTIONS_REPO = env_s3_config('SUBSCRIPTIONS_REPO')
CHANNEL_REPO = env_s3_config('CHANNEL_REPO')

ENDPOINT = env('ENDPOINT', default='AU')

TOPIC_BASE_URL = env_base_url('TOPIC_BASE_URL')
TOPIC_HUB_PATH = env_base_url('TOPIC_HUB_PATH')
HUB_URL = env('HUB_URL')

SERVICE_NAME = env('SERVICE_NAME', default='ethereum-channel-websub-hub')
SERVER_NAME = '0.0.0.0:8080'

TESTING = env_bool('TESTING')
DEBUG = env_bool('DEBUG')
