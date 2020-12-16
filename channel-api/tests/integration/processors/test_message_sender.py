from unittest import mock
import pytest
from src.processors.message_sender import MessageSender
from web3.exceptions import TimeExhausted
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


@mock.patch('web3.eth.Eth.generateGasPrice')
def test_gas_price_refresh(generateGasPrice, messages_repo):
    refreshed_gas_price = 20
    generateGasPrice.side_effect = [10, refreshed_gas_price]
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
    assert generateGasPrice.call_count == 2
    assert processor.use_case.gas_price == refreshed_gas_price
    assert not messages_repo.get_job()


@mock.patch('web3.eth.Eth.sendRawTransaction')
@mock.patch('web3.eth.Eth.waitForTransactionReceipt')
@mock.patch('web3.eth.Eth.generateGasPrice')
def test_gas_price_increase(
    generateGasPrice,
    waitForTransactionReceipt,
    sendRawTransaction,
    messages_repo
):
    message = {
        'subject': 'subject',
        'predicate': 'predicate',
        'obj': 'obj',
        'sender': 'AU',
        'receiver': 'GB'
    }
    config = Config()
    config.BLOCKCHAIN_GAS_PRICE_REFRESH_RATE = 10
    config.BLOCKCHAIN_GAS_PRICE_INCREASE_FACTOR = 1.1
    generateGasPrice.return_value = 111
    processor = MessageSender(config)
    # testing gas price increase due to a timeout
    waitForTransactionReceipt.side_effect = TimeExhausted()
    messages_repo.post_job(message)
    assert not next(processor)
    waitForTransactionReceipt.assert_called_once()
    expected_gas_price = int(generateGasPrice.return_value * config.BLOCKCHAIN_GAS_PRICE_INCREASE_FACTOR)
    assert processor.use_case.gas_price == expected_gas_price
    # testing gas price increase due to an underpriced transaction error
    waitForTransactionReceipt.reset_mock()
    sendRawTransaction.reset_mock()
    waitForTransactionReceipt.side_effect = None
    sendRawTransaction.side_effect = ValueError({'message': 'replacement transaction underpriced'})
    messages_repo.post_job(message)
    assert not next(processor)
    waitForTransactionReceipt.assert_not_called()
    sendRawTransaction.assert_called_once()
    expected_gas_price = int(expected_gas_price * config.BLOCKCHAIN_GAS_PRICE_INCREASE_FACTOR)
