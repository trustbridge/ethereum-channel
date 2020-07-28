from src.processors.new_messages_observer import NewMessagesObserver
from src.processors.callback_spreader import CallbackSpreader
from src.processors.callback_delivery import CallbackDelivery
from http import HTTPStatus
from unittest import mock


@mock.patch('src.use_cases.requests')
@mock.patch('src.api.views.requests')
@mock.patch('src.api.views.uuid')
def test(
    uuid,
    views_requests,
    use_case_requests,
    client,
    app,
    subscriptions_repo,
    notifications_repo,
    delivery_outbox_repo,
    channel_repo
):
    # subscribing to notifications by jurisdiction
    challenge = 'xxxx'
    topic = 'AU'
    uuid.uuid4.return_value = challenge
    callback_url = 'https://subsribers.com/1/callback'
    views_response_mock = mock.MagicMock()
    views_response_mock.status_code = 200
    views_response_mock.text = challenge
    views_requests.get.return_value = views_response_mock
    url = '/messages/subscriptions/by_jurisdiction'
    request_data = {
        'hub.callback': callback_url,
        'hub.topic': topic,
        'hub.lease_seconds': 36000
    }

    views_requests.reset_mock()
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
            'receiver': 'AU'
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
    with app.app_context():
        request_header = {
            'Link': f'<{app.config["HUB_URL"]}>; rel="hub"'
        }
    # confirming that message was delivered
    use_case_requests.post.assert_called_once_with(callback_url, json={'id': message['id']}, headers=request_header)
