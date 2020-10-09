from .. import config
from libtrustbridge.repos.elasticmqrepo import ElasticMQRepo
from libtrustbridge.repos.miniorepo import MinioRepo


def ChannelRepo(conf=None):
    conf = conf if conf is not None else config.CHANNEL_REPO
    return ElasticMQRepo(conf)


def ContractRepo(conf=None):
    conf = conf if conf is not None else config.CONTRACT_REPO
    return MinioRepo(conf)
