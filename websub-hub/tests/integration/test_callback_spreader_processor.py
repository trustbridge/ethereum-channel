from libtrustbridge.websub.domain import Pattern
from src.processors.callback_spreader import CallbackSpreader


def test(
    subscriptions_repo,
    delivery_outbox_repo,
    notifications_repo
):
    processor = CallbackSpreader()
    subscribers = [
        'subscriber/1',
        'subscriber/2'
    ]
    topic = 'aaa.bbb'
    job = {
        'topic': topic,
        'content': {
            'id': 'transaction-hash'
        }
    }

    assert subscriptions_repo._unsafe_is_empty_for_test()
    assert delivery_outbox_repo._unsafe_is_empty_for_test()
    assert notifications_repo._unsafe_is_empty_for_test()
    next(processor)
    assert subscriptions_repo._unsafe_is_empty_for_test()
    assert delivery_outbox_repo._unsafe_is_empty_for_test()
    assert notifications_repo._unsafe_is_empty_for_test()

    for url in subscribers:
        subscriptions_repo.subscribe_by_pattern(Pattern(topic), url, 300000)
    notifications_repo.post_job(job)
    next(processor)
    for i in range(2):
        queue_job = delivery_outbox_repo.get_job()
        assert queue_job
        queue_msg_id, queue_job = queue_job
        assert queue_job['s'] in subscribers
        assert queue_job['payload'] == job['content']
        assert queue_job['topic'] == topic
    assert not delivery_outbox_repo.get_job()
