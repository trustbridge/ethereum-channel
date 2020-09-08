import random
import urllib
import uuid
import requests
from http import HTTPStatus
import marshmallow
from libtrustbridge.websub import exceptions
from libtrustbridge import errors
from libtrustbridge.websub import constants
from libtrustbridge.websub import repos
from libtrustbridge.websub.schemas import SubscriptionForm
from libtrustbridge.websub.domain import Pattern
from src.repos import ChannelRepo
from src.loggers import logger


class ProcessSubscriptionFormDataUseCase:

    def _verify_subscription_callback(self, data):
        challenge = str(uuid.uuid4())
        params = {
            'hub.mode': data['mode'],
            'hub.topic': data['topic'],
            'hub.challenge': challenge,
            'hub.lease_seconds': data['lease_seconds']
        }
        response = requests.get(data['callback'], params)
        if response.status_code == HTTPStatus.OK and response.text == challenge:
            return
        raise exceptions.CallbackURLValidationError()

    def execute(self, form_data):

        try:
            data = SubscriptionForm().load(form_data)
        except marshmallow.ValidationError as e:
            raise errors.ValidationError(detail=str(e)) from e

        if data['mode'] == constants.MODE_ATTR_SUBSCRIBE_VALUE:
            self._verify_subscription_callback(data)

        return data


class SubscriptionBaseUseCase:

    def __init__(self, subscriptions_repo: repos.SubscriptionsRepo, topic_base_url: str):
        self.subscriptions_repo = subscriptions_repo
        # assuming the next structure of topic url, "base_url/{topic}"
        # preventing potential typo by adding missing trailing slash
        self.topic_base_url = topic_base_url if topic_base_url.endswith('/') else f'{topic_base_url}/'

    def _try_to_parse_canonical_url_topic(self, topic, prefix=None, suffix=None):
        # if url.scheme can't be determined topic is a plain string
        if not urllib.parse.urlparse(topic).scheme:
            return topic

        # expected topic url format "base_url/{topic}"
        if not topic.startswith(self.topic_base_url):
            raise errors.ValidationError(detail=f'Topic base url does not match expected value "{self.topic_base_url}"')

        # parsing expected topic url response text
        expected_topic = topic[len(self.topic_base_url):]
        # adding prefix and suffix
        if prefix:
            expected_topic = f'{prefix}.{expected_topic}'
        if suffix:
            expected_topic = f'{expected_topic}.{suffix}'
        # performing basic validation on the expected topic response
        try:
            Pattern(expected_topic)._validate()
        except ValueError as e:
            raise errors.ValidationError(
                detail=f'Expected topic "{expected_topic}" is an invalid pattern',
                source=str(e)
            ) from e
        # recreating the url with added suffix and prefix
        topic = self.topic_base_url + expected_topic
        # requesting channel topic existence confirmation
        response = requests.get(topic)

        if response.status_code == HTTPStatus.OK:
            topic = response.text
            if topic != expected_topic:
                raise errors.ValidationError(detail=f'Response topic "{topic}" != expected topic "{expected_topic}"')
        # if topic url contains invalid topic it will return NOT_FOUND response
        elif response.status_code == HTTPStatus.NOT_FOUND:
            raise errors.ValidationError(detail=f'Topic "{topic}" does not exist on the channel')
        # if for some reason topic url returns not 200 or 404 code we consider that this is unexpected response
        elif response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR:
            raise errors.ValidationError(detail=f'"{topic}" unexpected response, status_code "{response.status_code}"')
        else:
            raise errors.ValidationError(detail=f'Unable to test "{topic}", status code "{response.status_code}"')

        return topic

    def execute(self):
        raise NotImplementedError()


class SubscriptionRegisterUseCase(SubscriptionBaseUseCase):
    """
    Used by the subscription API

    Initialised with the subscription repo,
    saves callback url, pattern, expiration to the storage.
    """

    def execute(self, callback=None, topic=None, topic_prefix=None, expiration=None):
        # this operation deletes all previous subscription for given url and pattern
        # and replaces them with new one. Techically it's create or update operation
        topic = self._try_to_parse_canonical_url_topic(topic)
        if topic_prefix:
            topic = f'{topic_prefix}.{topic}'
        self.subscriptions_repo.subscribe_by_pattern(Pattern(topic), callback, expiration)


class SubscriptionDeregisterUseCase(SubscriptionBaseUseCase):
    """
    Used by the subscription API

    Remove subscription of a callback url to a topic
    """
    def execute(self, callback=None, topic=None, topic_prefix=None):
        topic = self._try_to_parse_canonical_url_topic(topic)
        if topic_prefix:
            topic = f'{topic_prefix}.{topic}'
        pattern = Pattern(topic)
        subscriptions = self.subscriptions_repo.get_subscriptions_by_pattern(pattern)
        subscriptions_by_callbacks = [s for s in subscriptions if s.callback_url == callback]
        if not subscriptions_by_callbacks:
            raise exceptions.SubscriptionNotFoundError()
        self.subscriptions_repo.bulk_delete([pattern.to_key(callback)])


class PostNotificationUseCase:
    """
    Base use case to send message for notification
    """

    def __init__(self, notification_repo: repos.NotificationsRepo):
        self.notifications_repo = notification_repo

    def publish(self, message):
        topic = self.get_topic(message)
        job_payload = {
            'topic': topic,
            'content': {
                'id': message['id']
            }
        }
        logger.debug('publish notification %r', job_payload)
        self.notifications_repo.post_job(job_payload)

    @staticmethod
    def get_topic(message):
        raise NotImplementedError


class PublishNewMessageUseCase(PostNotificationUseCase):
    """
    Given new message,
    message id should be posted for notification"""

    @staticmethod
    def get_topic(message):
        return f"jurisdiction.{message['message']['receiver']}"


class NewMessagesNotifyUseCase:
    """
    Query shared database in order to receive new messages directed
    to the endpoint and send notification for each message.
    """

    def __init__(self, receiver, channel_repo: ChannelRepo, notifications_repo: repos.NotificationsRepo):
        self.channel_repo = channel_repo
        self.notifications_repo = notifications_repo
        self.receiver = receiver

    def execute(self):
        # receiving MessageResponse dict from channel-api
        queue_message = self.channel_repo.get_job()
        if not queue_message:
            return False
        queue_msg_id, message = queue_message
        # filtering messages based on the receiver property
        # if we're not the receiver we must skip a message
        if message['message']['receiver'] != self.receiver:
            return
        PublishNewMessageUseCase(self.notifications_repo).publish(message)
        self.channel_repo.delete(queue_msg_id)
        return True


class InvalidCallbackResponse(Exception):
    pass


class DispatchMessageToSubscribersUseCase:
    """
    Used by the callbacks spreader worker.

    This is the "fan-out" part of the WebSub,
    where each event dispatched
    to all the relevant subscribers.
    For each event (notification),
    it looks-up the relevant subscribers
    and dispatches a callback task
    so that they will be notified.

    There is a downstream delivery processor
    that actually makes the callback,
    it is insulated from this process
    by the delivery outbox message queue.

    """

    def __init__(
            self, notifications_repo: repos.NotificationsRepo,
            delivery_outbox_repo: repos.DeliveryOutboxRepo,
            subscriptions_repo: repos.SubscriptionsRepo):
        self.notifications = notifications_repo
        self.delivery_outbox = delivery_outbox_repo
        self.subscriptions = subscriptions_repo

    def execute(self):
        job = self.notifications.get_job()
        if not job:
            return
        return self.process(*job)

    def process(self, msg_id, payload):
        content = payload['content']
        topic = payload['topic']

        subscriptions = self._get_subscriptions(topic)

        for subscription in subscriptions:
            if not subscription.is_valid:
                continue
            job = {
                's': subscription.callback_url,
                'topic': topic,
                'payload': content,
            }
            logger.info("Scheduling notification of \n[%s] with the content \n%s", subscription.callback_url, content)
            self.delivery_outbox.post_job(job)

        self.notifications.delete(msg_id)

    def _get_subscriptions(self, topic):
        pattern = repos.Pattern(topic)
        subscribers = self.subscriptions.get_subscriptions_by_pattern(pattern)
        if not subscribers:
            logger.info("Nobody to notify about the topic %s", topic)
        return subscribers


class DeliverCallbackUseCase:
    """
    Is used by a callback deliverer worker

    Reads queue delivery_outbox_repo consisting of tasks in format:
        (url, message)

    Then such message should be either sent to this URL and the task is deleted
    or, in case of any error, not to be re-scheduled again
    (up to MAX_ATTEMPTS times)

    """

    MAX_ATTEMPTS = 3

    def __init__(self, delivery_outbox_repo: repos.DeliveryOutboxRepo, hub_url: str, topic_hub_path: str):
        self.delivery_outbox = delivery_outbox_repo
        self.topic_hub_path = topic_hub_path if topic_hub_path.endswith('/') else f'{topic_hub_path}/'
        self.hub_url = hub_url

    def execute(self):
        deliverable = self.delivery_outbox.get_job()
        if not deliverable:
            return

        queue_msg_id, payload = deliverable
        return self.process(queue_msg_id, payload)

    def process(self, queue_msg_id, job):
        subscribe_url = job['s']
        payload = job['payload']
        topic = job['topic']
        attempt = int(job.get('retry', 1))
        try:
            logger.debug('[%s] deliver notification to %s with payload: %s, topic: %s (attempt %s)',
                         queue_msg_id, subscribe_url, payload, topic, attempt)
            self._deliver_notification(subscribe_url, payload, topic)
        except InvalidCallbackResponse as e:
            logger.info("[%s] delivery failed", queue_msg_id)
            logger.exception(e)
            if attempt < self.MAX_ATTEMPTS:
                logger.info("[%s] re-schedule delivery", queue_msg_id)
                self._retry(subscribe_url, payload, topic, attempt)

        self.delivery_outbox.delete(queue_msg_id)

    def _retry(self, subscribe_url, payload, topic, attempt):
        logger.info("Delivery failed, re-schedule it")
        job = {'s': subscribe_url, 'payload': payload, 'retry': attempt + 1, 'topic': topic}
        self.delivery_outbox.post_job(job, delay_seconds=self._get_retry_time(attempt))

    def _deliver_notification(self, url, payload, topic):
        """
        Send the payload to subscriber's callback url

        https://indieweb.org/How_to_publish_and_consume_WebSub
        https://www.w3.org/TR/websub/#x7-content-distribution
        """

        logger.info("Sending WebSub payload \n    %s to callback URL \n    %s", payload, url)
        topic_self_url = urllib.parse.urljoin(self.topic_hub_path, topic)
        header = {
            'Link': f'<{self.hub_url}>; rel="hub", <{topic_self_url}>; rel="self"'
        }
        try:
            resp = requests.post(url, json=payload, headers=header)
            if str(resp.status_code).startswith('2'):
                return
        except ConnectionError:
            raise InvalidCallbackResponse("Connection error, url: %s", url)

        raise InvalidCallbackResponse("Subscription url %s seems to be invalid, "
                                      "returns %s", url, resp.status_code)

    @staticmethod
    def _get_retry_time(attempt):
        """exponential back off with jitter"""
        base = 8
        max_retry = 100
        delay = min(base * 2 ** attempt, max_retry)
        jitter = random.uniform(0, delay / 2)
        return int(delay / 2 + jitter)
