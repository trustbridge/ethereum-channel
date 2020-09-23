import pytest
from libtrustbridge.websub.domain import Pattern
from http import HTTPStatus
from unittest import mock
from tests import conftest


@mock.patch('src.use_cases.requests')
@mock.patch('src.use_cases.uuid')
@pytest.mark.parametrize('url,topic,pattern,topic_response', [
    ['/messages/subscriptions/by_id', 'a.b.c', 'a.b.c', None],
    ['/messages/subscriptions/by_id', f'{conftest.TOPIC_BASE_URL}a.b.c', 'a.b.c', 'a.b.c'],
    ['/messages/subscriptions/by_jurisdiction', 'a.b.c', 'jurisdiction.a.b.c', None],
])
def test_subscribe(uuid, requests, client, subscriptions_repo, url, topic, pattern, topic_response):
    # pattern used to get subscriptions from the subscription repo
    # topic  used to create subscriptions
    # url used to post subscribe/unsubscribe requests

    callback_url = 'https://subsribers.com/1/callback'

    challenge_response_mock = mock.MagicMock()
    challenge_response_mock.status_code = 200
    challenge_response_mock.text = uuid.uuid4.return_value = 'xxxx'

    failed_challenge_response_mock = mock.MagicMock()
    failed_challenge_response_mock.status_code = 400

    topic_response_mock = mock.MagicMock()
    topic_response_mock.status_code = 200
    topic_response_mock.text = topic_response
    if topic_response is not None:
        assert topic_response == topic[len(conftest.TOPIC_BASE_URL):]

    # first call used to verify callback url
    # second call used when topic is a canonical url and requires verification via get request
    requests.get.side_effect = [challenge_response_mock, topic_response_mock]
    request_data = {
        'hub.callback': callback_url,
        'hub.topic': topic,
        'hub.lease_seconds': 36000
    }

    # creating subscription
    requests.reset_mock()
    response = client.post(
        url,
        data={**request_data, 'hub.mode': 'subscribe'},
        mimetype='application/x-www-form-urlencoded'
    )
    requests.get.assert_called()
    assert response.status_code == HTTPStatus.ACCEPTED
    # checking that subscription successfully created
    subscriptions = subscriptions_repo.get_subscriptions_by_pattern(Pattern(pattern))
    assert subscriptions
    assert len(subscriptions) == 1
    assert list(subscriptions)[0].callback_url == callback_url

    # deleting subscription
    requests.reset_mock()
    requests.get.side_effect = [topic_response_mock]
    response = client.post(
        url,
        data={**request_data, 'hub.mode': 'unsubscribe'},
        mimetype='application/x-www-form-urlencoded'
    )
    assert response.status_code == HTTPStatus.ACCEPTED
    # checking that subscription successfully deleted
    subscriptions = subscriptions_repo.get_subscriptions_by_pattern(Pattern(pattern))
    assert not subscriptions

    # testing unsubscribe from non existing subscription
    requests.reset_mock()
    requests.get.side_effect = [topic_response_mock]
    response = client.post(
        url,
        data={**request_data, 'hub.mode': 'unsubscribe'},
        mimetype='application/x-www-form-urlencoded'
    )
    assert response.status_code == HTTPStatus.NOT_FOUND

    # testing failed callback url challenge
    requests.reset_mock()
    requests.get.side_effect = [failed_challenge_response_mock]
    response = client.post(
        url,
        data={**request_data, 'hub.mode': 'subscribe'},
        mimetype='application/x-www-form-urlencoded'
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST

    # testing invalid hub mode
    requests.reset_mock()
    response = client.post(
        url,
        data={**request_data, 'hub.mode': 'unknownmode'},
        mimetype='application/x-www-form-urlencoded'
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
