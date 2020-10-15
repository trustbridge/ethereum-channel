from .config import Config
from libtrustbridge.repos.elasticmqrepo import ElasticMQRepo
from libtrustbridge.repos.miniorepo import MinioRepo


def Channel() -> ElasticMQRepo:
    return ElasticMQRepo(Config().CHANNEL_REPO)


def Contract() -> MinioRepo:
    return MinioRepo(Config().CONTRACT_REPO)
