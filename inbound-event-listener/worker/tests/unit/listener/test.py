import os
import tempfile
from unittest import mock
from src.listener import Listener


@mock.patch('src.listener.Web3')
def test_duplicates_avoidance(Web3):

    EVENT_NAME = 'TestEvent'
    LISTENER_ID = 'TestListenerId'
    RECEIVER_ID = 'TestReceiverId'
    LISTENER_BLOCKS_LOG_DIR = tempfile.mkdtemp()
    FROM_BLOCK = 2

    receiver = mock.MagicMock()
    receiver.Id = RECEIVER_ID
    receivers = {RECEIVER_ID: receiver}

    config = mock.MagicMock()
    config.Id = LISTENER_ID
    config.Event.Name = EVENT_NAME
    config.Event.Filter = {}
    config.Receivers = [RECEIVER_ID]

    global_config = mock.MagicMock()
    global_config.Worker.General.ListenerBlocksLogDir = LISTENER_BLOCKS_LOG_DIR

    contract = mock.MagicMock()

    event_filter = mock.MagicMock()
    event_filter.get_all_entries.return_value = []

    event = mock.MagicMock()
    event.createFilter = mock.MagicMock()
    event.createFilter.return_value = event_filter

    contract.events = {
        EVENT_NAME: event
    }

    with open(os.path.join(LISTENER_BLOCKS_LOG_DIR, LISTENER_ID), 'wt+') as f:
        f.write(str(FROM_BLOCK))

    listener = Listener(contract, receivers, config, global_config)

    event.createFilter.assert_called()
    listener.poll()
    event_filter.get_all_entries.assert_called()
    receiver.send.assert_not_called()

    event.reset_mock()
    event_filter.reset_mock()
    receiver.reset_mock()

    e = mock.MagicMock()
    e.blockNumber = FROM_BLOCK - 1
    event_filter.get_all_entries.return_value = [e]
    listener.poll()
    event_filter.get_all_entries.assert_called()
    receiver.send.assert_not_called()

    event.reset_mock()
    event_filter.reset_mock()
    receiver.reset_mock()

    e.blockNumber = FROM_BLOCK
    listener.poll()
    event_filter.get_all_entries.assert_called()
    receiver.send.assert_called()
