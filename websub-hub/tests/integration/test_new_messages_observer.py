from src.processors.new_messages_observer import NewMessagesObserver


def test(
    notifications_repo,
    channel_repo
):
    message = {
        'id': 'transaction hash',
        'status': 'received',
        'message': {
            'receiver': 'AU'
        }
    }
    processor = NewMessagesObserver()
    # empty repos, the processor should do nothing
    assert notifications_repo._unsafe_is_empty_for_test()
    assert channel_repo._unsafe_is_empty_for_test()
    next(processor)
    assert notifications_repo._unsafe_is_empty_for_test()
    assert channel_repo._unsafe_is_empty_for_test()
    # a job posted to the channel repo, the processor must post a job to the notifications repo.
    channel_repo.post_job(message)
    next(processor)
    assert not channel_repo.get_job()
    queue_message = notifications_repo.get_job()
    assert queue_message
    queue_message_id, job = queue_message
    assert job == {
        'topic': f"jurisdiction.{message['message']['receiver']}",
        'content': {
            'id': message['id']
        }
    }
    # a channel repo message must be deleted after the successful processing
    assert channel_repo._unsafe_is_empty_for_test()
