from unittest import mock
import pytest
from libtrustbridge import errors
from src.use_cases import DeliverCallbackUseCase, SubscriptionBaseUseCase


def test_deliver_callback_get_retry_time():
    attempts = [0, 0, 0, 0]
    for i in range(0, 1000):
        attempts[1] = DeliverCallbackUseCase._get_retry_time(1)
        attempts[2] = DeliverCallbackUseCase._get_retry_time(2)
        attempts[3] = DeliverCallbackUseCase._get_retry_time(3)
        assert 8 <= attempts[1] <= 16
        assert 16 <= attempts[2] <= 32
        assert 32 <= attempts[3] <= 64
        assert attempts[1] < attempts[2] < attempts[3]


@mock.patch('src.use_cases.requests')
def test_subscription_base_use_case(requests):
    response = mock.MagicMock()
    requests.get.return_value = response

    topic_base_url = 'http://channel-api.au/'
    use_case = SubscriptionBaseUseCase(None, topic_base_url)

    # testing topic url parsing without prefix
    topic = 'a.b.c'
    topic_url = f'{topic_base_url}{topic}'
    response.text = 'a.b.c'
    response.status_code = 200
    assert use_case._try_to_parse_canonical_url_topic(topic_url) == topic
    # testing topic url parsing with suffix and prefix
    topic = 'a.b.c'
    topic_url = f'{topic_base_url}{topic}'
    suffix = 'suffix'
    prefix = 'prefix'
    topic = f'{prefix}.{topic}.{suffix}'
    response.text = topic
    assert use_case._try_to_parse_canonical_url_topic(topic_url, prefix, suffix) == topic

    # testing invalid expected topic
    with pytest.raises(errors.ValidationError) as einfo:
        topic = 'a/a.b'
        topic_url = f'{topic_base_url}{topic}'
        use_case._try_to_parse_canonical_url_topic(topic_url)
    assert einfo.value.kwargs['detail'] == f'Expected topic "{topic}" is an invalid pattern'

    # testing wrong base url
    with pytest.raises(errors.ValidationError) as einfo:
        topic = 'a.b.c'
        topic_url = f'http://wrong.base.url/{topic}'
        use_case._try_to_parse_canonical_url_topic(topic_url)
    assert einfo.value.kwargs['detail'] == f'Topic base url does not match expected value "{topic_base_url}"'

    # testing unexpected response.text
    with pytest.raises(errors.ValidationError) as einfo:
        topic = 'a.b.c'
        topic_url = f'{topic_base_url}{topic}'
        response.text = 'unexpected topic response'
        use_case._try_to_parse_canonical_url_topic(topic_url)
    assert einfo.value.kwargs['detail'] == f'Response topic "{response.text}" != expected topic "{topic}"'

    # testing topic url returns 404
    with pytest.raises(errors.ValidationError) as einfo:
        topic = 'a.b.c'
        topic_url = f'{topic_base_url}{topic}'
        response.status_code = 404
        use_case._try_to_parse_canonical_url_topic(topic_url)
    assert einfo.value.kwargs['detail'] == f'Topic "{topic_url}" does not exist on the channel'

    # testing topic url returns 405, <= 500 unexpected response code
    with pytest.raises(errors.ValidationError) as einfo:
        topic = 'a.b.c'
        topic_url = f'{topic_base_url}{topic}'
        response.status_code = 405
        use_case._try_to_parse_canonical_url_topic(topic_url)
    assert einfo.value.kwargs['detail'] == f'"{topic_url}" unexpected response, status_code "{response.status_code}"'

    # testing topic url returns >= 500, unexpected internal server error
    with pytest.raises(errors.ValidationError) as einfo:
        topic = 'a.b.c'
        topic_url = f'{topic_base_url}{topic}'
        response.status_code = 501
        use_case._try_to_parse_canonical_url_topic(topic_url)
    assert einfo.value.kwargs['detail'] == f'Unable to test "{topic_url}", status code "{response.status_code}"'
