import pytest
from libtrustbridge.websub.domain import Pattern
from http import HTTPStatus
from unittest import mock


@mock.patch('src.api.views.requests')
@mock.patch('src.api.views.uuid')
@pytest.mark.parametrize('url,pattern', [
    ['/messages/subscriptions/by_id', 'a.b.c'],
    ['/messages/subscriptions/by_jurisdiction', 'jurisdiction.a.b.c'],
])
def test_subscribe(uuid, requests, client, subscriptions_repo, url, pattern):
    challenge = 'xxxx'
    topic = 'a.b.c'
    uuid.uuid4.return_value = challenge
    callback_url = 'https://subsribers.com/1/callback'
    response_mock = mock.MagicMock()
    response_mock.status_code = 200
    response_mock.text = challenge
    requests.get.return_value = response_mock
    request_data = {
        'hub.callback': callback_url,
        'hub.topic': topic,
        'hub.lease_seconds': 36000
    }

    requests.reset_mock()
    response = client.post(
        url,
        data={**request_data, 'hub.mode': 'subscribe'},
        mimetype='application/x-www-form-urlencoded'
    )
    requests.get.assert_called_once()
    assert response.status_code == HTTPStatus.ACCEPTED
    subscriptions = subscriptions_repo.get_subscriptions_by_pattern(Pattern(pattern))
    assert subscriptions
    assert len(subscriptions) == 1
    assert list(subscriptions)[0].callback_url == callback_url

    requests.reset_mock()
    response = client.post(
        url,
        data={**request_data, 'hub.mode': 'unsubscribe'},
        mimetype='application/x-www-form-urlencoded'
    )
    assert response.status_code == HTTPStatus.ACCEPTED
    subscriptions = subscriptions_repo.get_subscriptions_by_pattern(Pattern(topic))
    assert not subscriptions

    requests.reset_mock()
    response = client.post(
        url,
        data={**request_data, 'hub.mode': 'unsubscribe'},
        mimetype='application/x-www-form-urlencoded'
    )
    assert response.status_code == HTTPStatus.NOT_FOUND

    requests.reset_mock()
    response_mock.status_code = 400
    response = client.post(
        url,
        data={**request_data, 'hub.mode': 'subscribe'},
        mimetype='application/x-www-form-urlencoded'
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST

    requests.reset_mock()
    response = client.post(
        url,
        data={**request_data, 'hub.mode': 'unknownmode'},
        mimetype='application/x-www-form-urlencoded'
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
