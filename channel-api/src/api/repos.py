from box import Box
from libtrustbridge.websub.repos import SubscriptionsRepo
from libtrustbridge.repos.elasticmqrepo import ElasticMQRepo
from libtrustbridge.repos.miniorepo import MinioRepo


def Channel(config: Box = None) -> ElasticMQRepo:
    return ElasticMQRepo(config)


def Contract(config: Box = None) -> MinioRepo:
    return MinioRepo(config)


def Subscriptions(config: Box = None) -> SubscriptionsRepo:
    return SubscriptionsRepo(config)
