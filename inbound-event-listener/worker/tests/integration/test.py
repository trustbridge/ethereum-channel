import os
import json
from unittest import mock
import pytest
from src.worker import Worker


@pytest.fixture(scope='function', params=[
    '/worker/tests/data/config.yml',
    '/worker/tests/data/config.json'
])
def valid_config_filename(request):
    return request.param


def test_sqs_receiver(emitEvent, get_sqs_msgs, valid_config_filename):
    with mock.patch.dict(os.environ, {'CONFIG_FILE': valid_config_filename}):
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


def test_incorrect_config():
    def load_worker_with_config(config_file):
        with mock.patch.dict(os.environ, {'CONFIG_FILE': config_file}):
            return Worker()

    with pytest.raises(Exception) as einfo:
        load_worker_with_config('/worker/tests/data/invalid-receiver.yml')
    assert str(einfo.value) == "{'Receivers': {0: [\"Can't deserialize the field using any known receiver schema\"]}}"

    with pytest.raises(Exception) as einfo:
        load_worker_with_config('/worker/tests/data/missing-listener-receiver.yml')
    assert str(einfo.value) == 'Receiver "MissingReceiver" not found'
    with pytest.raises(Exception) as einfo:
        load_worker_with_config('/worker/tests/data/duplicate-receiver.yml')
    assert str(einfo.value) == "Reciver id duplicates found ['LogReceiver-1']"
    with pytest.raises(Exception) as einfo:
        load_worker_with_config('/worker/tests/data/duplicate-listener.yml')
    assert str(einfo.value) == "Listener id duplicates found ['EventOneListener']"

    with pytest.raises(Exception) as einfo:
        load_worker_with_config('/worker/tests/data/wrong-config-extension.conf')
    assert str(einfo.value) == 'Unsupported config file extension ".conf"'
