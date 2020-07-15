from libtrustbridge.utils.conf import env_s3_config, env_queue_config, env


NOTIFICATIONS_REPO = env_queue_config('NOTIFICATIONS_REPO')
DELIVERY_OUTBOX_REPO = env_queue_config('DELIVERY_OUTBOX_REPO')
SUBSCRIPTIONS_REPO = env_s3_config('SUBSCRIPTIONS_REPO')
CHANNEL_REPO = env_s3_config('CHANNEL_REPO')
ENDPOINT = env('ENDPOINT', default='AU')
