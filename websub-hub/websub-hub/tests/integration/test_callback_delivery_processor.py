import urllib
from unittest import mock
from src.processors.callback_delivery import CallbackDelivery
from tests import conftest


@mock.patch('src.use_cases.requests')
@mock.patch('src.use_cases.DeliverCallbackUseCase._get_retry_time')
def test(
    _get_retry_time,
    requests,
    delivery_outbox_repo,
    app
):
    topic = 'jurisdiction.AU'
    topic_self_url = urllib.parse.urljoin(conftest.TOPIC_HUB_PATH, topic)
    assert topic_self_url == '/topic/jurisdiction.AU'
    job = {
        's': None,
        'payload': {
            'id': 'transaction-hash'
        },
        'topic': topic
    }
    processor = CallbackDelivery()
    response = mock.MagicMock()
    response.status_code = 200
    requests.post.return_value = response
    with app.app_context():
        request_header = {
            'Link': f'<{conftest.HUB_URL}>; rel="hub", <{topic_self_url}>; rel="self"'
        }
    subscribers = [
        'subscriber/1',
        'subscriber/2',
        'subscriber/3'
    ]
    assert delivery_outbox_repo._unsafe_is_empty_for_test()
    # empty delivery outbox repo, the processor must do nothing
    next(processor)
    requests.post.assert_not_called()
    # the delivery outbox repo contains two jobs, must send jobs paylod to specified subscribers
    for url in subscribers:
        delivery_outbox_repo.post_job({**job, 's': url})
    for i in range(2):
        requests.reset_mock()
        next(processor)
        requests.post.assert_called_with(subscribers[i], json=job['payload'], headers=request_header)
        _get_retry_time.assert_not_called()
    # the next job callback returns 400 status code, the processor must initiate a retry
    for i in range(2):
        requests.reset_mock()
        _get_retry_time.reset_mock()
        response.status_code = 400
        _get_retry_time.return_value = 0
        next(processor)
        requests.post.assert_called_with(subscribers[2], json=job['payload'], headers=request_header)
        _get_retry_time.assert_called_with(i + 1)
    # max retries reached, the processor must discard the message, this time it will be a connection error
    requests.reset_mock()
    _get_retry_time.reset_mock()
    requests.post.side_effect = ConnectionError
    next(processor)
    requests.post.assert_called_with(subscribers[2], json=job['payload'], headers=request_header)
    _get_retry_time.assert_not_called()
    assert delivery_outbox_repo._unsafe_is_empty_for_test()
