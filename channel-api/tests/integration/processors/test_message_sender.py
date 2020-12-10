from unittest import mock
import pytest
from src.processors.message_sender import MessageSender
from src.processors.message_sender.config import Config


@pytest.mark.parametrize('gas_price_strategy', ('fast', 'medium', 'slow'))
def test(messages_repo, gas_price_strategy):
    config = Config()
    config.BLOCKCHAIN_GAS_PRICE_STRATEGY = gas_price_strategy
    processor = MessageSender(config)
    # no messages in the queue processor must do nothing
    assert not messages_repo.get_job()
    assert not next(processor)
    message = {
        'subject': 'subject',
        'predicate': 'predicate',
        'obj': 'obj',
        'sender': 'AU',
        'receiver': 'GB'
    }
    # one message in the queue, processor must create ethereum transaction
    messages_repo.post_job(message)
    assert next(processor)


@mock.patch('src.processors.message_sender.use_cases.ProcessMessageQueueUseCase.generate_gas_price')
def test_gas_price_refresh(generate_gas_price, messages_repo):
    refreshed_gas_price = 20
    generate_gas_price.side_effect = [10, refreshed_gas_price]
    message = {
        'subject': 'subject',
        'predicate': 'predicate',
        'obj': 'obj',
        'sender': 'AU',
        'receiver': 'GB'
    }
    config = Config()
    config.BLOCKCHAIN_GAS_PRICE_REFRESH_RATE = 10
    processor = MessageSender(config)
    for i in range(config.BLOCKCHAIN_GAS_PRICE_REFRESH_RATE):
        messages_repo.post_job(message)
        assert next(processor)
    assert generate_gas_price.call_count == 2
    assert processor.use_case.gas_price == refreshed_gas_price
    assert not messages_repo.get_job()
