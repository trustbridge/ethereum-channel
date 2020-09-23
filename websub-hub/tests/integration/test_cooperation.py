import urllib
from unittest import mock
from http import HTTPStatus
import pytest
from src.processors.new_messages_observer import NewMessagesObserver
from src.processors.callback_spreader import CallbackSpreader
from src.processors.callback_delivery import CallbackDelivery
from tests import conftest


JURISDICTION_TOPIC = f'jurisdiction.{conftest.ENDPOINT}'


@mock.patch('src.use_cases.requests')
@mock.patch('src.use_cases.uuid')
@pytest.mark.parametrize('url, subscription_topic, topic', [
    ('/messages/subscriptions/by_jurisdiction', conftest.ENDPOINT, JURISDICTION_TOPIC),
    ('/messages/subscriptions/by_id', JURISDICTION_TOPIC, JURISDICTION_TOPIC)
])
def test_subscriptions_by_jurisdiction(
    uuid,
    use_case_requests,
    client,
    app,
    subscriptions_repo,
    notifications_repo,
    delivery_outbox_repo,
    channel_repo,
    url,
    subscription_topic,
    topic
):
    # subscribing to notifications by jurisdiction
    challenge = 'xxxx'
    uuid.uuid4.return_value = challenge
    callback_url = 'https://subsribers.com/1/callback'
    use_case_response_mock = mock.MagicMock()
    use_case_response_mock.status_code = 200
    use_case_response_mock.text = challenge
    use_case_requests.get.return_value = use_case_response_mock
    request_data = {
        'hub.callback': callback_url,
        'hub.topic': subscription_topic,
        'hub.lease_seconds': 36000
    }

    use_case_requests.reset_mock()
    response = client.post(
        url,
        data={**request_data, 'hub.mode': 'subscribe'},
        mimetype='application/x-www-form-urlencoded'
    )
    assert response.status_code == HTTPStatus.ACCEPTED
    new_messages_observer = NewMessagesObserver()
    callback_spreader = CallbackSpreader()
    callback_delivery = CallbackDelivery()
    # new message observer processor receives new message
    message = {
        'id': 'transaction hash',
        'status': 'received',
        'message': {
            'receiver': conftest.ENDPOINT
        }
    }
    channel_repo.post_job(message)
    next(new_messages_observer)
    # new message observer sends a job to callback spreader
    next(callback_spreader)
    # callback spreader creates separate callback delivery job for each subscriber
    use_case_response_mock = mock.MagicMock()
    use_case_requests.post.return_value = use_case_response_mock
    use_case_response_mock.status_code = 200
    next(callback_delivery)
    # callback delivery processor sends payload using requests library to each subscriber
    topic_self_url = urllib.parse.urljoin(conftest.TOPIC_HUB_PATH, topic)
    request_header = {
        'Link': f'<{conftest.HUB_URL}>; rel="hub", <{topic_self_url}>; rel="self"'
    }
    # confirming that message was delivered
    use_case_requests.post.assert_called_once_with(callback_url, json={'id': message['id']}, headers=request_header)
