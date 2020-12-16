import json
from box import Box
from libtrustbridge.websub.repos import (
    SubscriptionsRepo,
    NotificationsRepo,
    DeliveryOutboxRepo
)
from libtrustbridge.repos.elasticmqrepo import ElasticMQRepo
from libtrustbridge.repos.miniorepo import MinioRepo


class Channel(ElasticMQRepo):
    def __init__(self, config: Box = None):
        super().__init__(config)


class Contract(MinioRepo):
    def __init__(self, config: Box = None):
        super().__init__(config)


class Subscriptions(SubscriptionsRepo):
    def __init__(self, config: Box = None):
        super().__init__(config)


class Notifications(NotificationsRepo):
    def __init__(self, config: Box = None):
        super().__init__(config)


class DeliveryOutbox(DeliveryOutboxRepo):
    def __init__(self, config: Box = None):
        super().__init__(config)


class Messages(ElasticMQRepo):
    def __init__(self, config: Box = None):
        super().__init__(config)

    def get_job(self, visibility_timeout=30):
        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            MessageAttributeNames=['payload'],
            MaxNumberOfMessages=1,
            VisibilityTimeout=visibility_timeout,
            WaitTimeSeconds=self.WAIT_FOR_MESSAGE_SECONDS
        )
        if "Messages" not in response.keys():
            return False
        if len(response["Messages"]) < 1:
            return False
        queue_message_id = response["Messages"][0]["ReceiptHandle"]
        payload = json.loads(response["Messages"][0]["Body"])
        return (queue_message_id, payload)
