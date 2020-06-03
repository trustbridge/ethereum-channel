import os
import json
from unittest import mock
from src.worker import Worker


def test(emitEvent, get_sqs_msgs):
    with mock.patch.dict(os.environ, {'CONFIG_FILE': '/worker/tests/data/config.yml'}):
        worker = Worker()
    # EventOne must go to the queue-1, but not queue-2
    emitEvent(1, 'EventOne')
    worker.poll()
    message = get_sqs_msgs(0)
    assert message
    assert len(message) == 1
    assert json.loads(message[0].body)['args']['message'] == 'EventOne'
    assert not get_sqs_msgs(1)
    message[0].delete()
    # EventOne must go to the queue-2, but not queue-1
    emitEvent(2, 'EventTwo')
    worker.poll()
    message = get_sqs_msgs(1)
    assert message
    assert len(message) == 1
    assert json.loads(message[0].body)['args']['message'] == 'EventTwo'
    assert not get_sqs_msgs(0)
    message[0].delete()
    # EventThree must be received by both queue-1 and queue-2
    emitEvent(3, 'EventThree')
    worker.poll()
    messages = [
        get_sqs_msgs(0),
        get_sqs_msgs(1)
    ]
    assert len(messages[0]) == 1
    assert len(messages[0]) == len(messages[1])
    assert messages[0][0].body == messages[1][0].body
    assert json.loads(messages[0][0].body)['args']['message'] == 'EventThree'
    messages[0][0].delete()
    messages[1][0].delete()
    # EventFour must not be received by queue-1 or queue-2
    emitEvent(3, 'EventThree')
    assert not get_sqs_msgs(0)
    assert not get_sqs_msgs(1)
