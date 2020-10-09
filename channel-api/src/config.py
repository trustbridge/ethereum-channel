import os
from libtrustbridge.utils.conf import env_s3_config, env_queue_config


AWS_ENDPOINT_URL = os.environ.get('AWS_ENDPOINT_URL')
HTTP_BLOCKCHAIN_ENDPOINT = os.environ['HTTP_BLOCKCHAIN_ENDPOINT']

CONTRACT_BUILD_ARTIFACT_KEY = os.environ['CONTRACT_BUILD_ARTIFACT_KEY']
CONTRACT_NETWORK_ID = str(int(os.environ['CONTRACT_NETWORK_ID']))
CONTRACT_OWNER_PRIVATE_KEY = os.environ['CONTRACT_OWNER_PRIVATE_KEY']

CONTRACT_REPO = env_s3_config('CONTRACT_REPO')
NOTIFICATIONS_REPO = env_queue_config('NOTIFICATIONS_REPO')
DELIVERY_OUTBOX_REPO = env_queue_config('DELIVERY_OUTBOX_REPO')
SUBSCRIPTIONS_REPO = env_s3_config('SUBSCRIPTIONS_REPO')
CHANNEL_REPO = env_queue_config('CHANNEL_REPO')

SENDER_REF = os.environ['SENDER_REF']
SENDER = os.environ['SENDER']
