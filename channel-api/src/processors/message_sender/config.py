from box import Box
from libtrustbridge.utils.conf import env_s3_config, env, string_or_b64kms, env_queue_config


def Config():
    environment_config = dict(
        HTTP_BLOCKCHAIN_ENDPOINT=env('HTTP_BLOCKCHAIN_ENDPOINT'),
        BLOCKCHAIN_GAS_PRICE_STRATEGY=env('BLOCKCHAIN_GAS_PRICE_STRATEGY', 'fast').lower(),
        BLOCKCHAIN_GAS_PRICE_REFRESH_RATE=int(env('BLOCKCHAIN_GAS_PRICE_REFRESH_RATE', default=10)),

        CONTRACT_REPO=env_s3_config('CONTRACT_REPO'),
        CONTRACT_BUILD_ARTIFACT_KEY=env('CONTRACT_BUILD_ARTIFACT_KEY'),
        CONTRACT_NETWORK_ID=str(int(env('CONTRACT_NETWORK_ID', default=1))),

        SENDER_ACCOUNT_PRIVATE_KEY=string_or_b64kms(env('SENDER_ACCOUNT_PRIVATE_KEY')),

        MESSAGES_REPO=env_queue_config('MESSAGES_REPO')
    )
    return Box(environment_config)
