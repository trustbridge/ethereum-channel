from libtrustbridge.repos.elasticmqrepo import ElasticMQRepo


class ChannelRepo(ElasticMQRepo):
    def _get_queue_name(self):
        return 'channel'
