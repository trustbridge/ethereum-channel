from web3.gas_strategies.time_based import (
    fast_gas_price_strategy,
    medium_gas_price_strategy,
    slow_gas_price_strategy
)
from web3.exceptions import TimeExhausted
from src.loggers import logging


class UnderpricedReplacementTransactionException(Exception):
    pass


class ProcessMessageQueueUseCase:

    logger = logging.getLogger('ProcessMessageQueueUseCase')

    def __init__(
        self,
        messages_repo=None,
        web3=None,
        contract=None,
        sender_private_key=None,
        gas_price_strategy=None,
        gas_price_refresh_rate=None,
        gas_price_increase_factor=None
    ):
        self.web3 = web3
        self.contract = contract
        self.sender_private_key = sender_private_key
        self.sender_public_key = self.web3.eth.account.from_key(self.sender_private_key).address
        self.messages_repo = messages_repo
        self.gas_price_refresh_rate = gas_price_refresh_rate
        self.gas_price_increase_factor = gas_price_increase_factor
        self.validate_configuration()
        self.set_gas_price_strategy(gas_price_strategy)
        self.update_gas_price()

    def validate_configuration(self):
        if self.gas_price_refresh_rate < 1:
            raise ValueError('gas price refresh rate must be >= 1')
        if self.gas_price_increase_factor < 1:
            raise ValueError('gas price increase factor must be > 1')

    def execute(self):
        job = self.messages_repo.get_job(visibility_timeout=self.message_visibility_timeout)
        if not job:
            return False
        job_id, message = job
        self.refresh_gas_price()
        try:
            self.send_message(message)
            self.messages_repo.delete(job_id)
            self.transactions_count += 1
            return True
        except TimeExhausted:
            self.logger.warn('transaction timed out, increasing gas price')
            self.increase_gas_price()
            return False
        except UnderpricedReplacementTransactionException:
            self.logger.warn('underpriced replacement transaction, increasing gas price')
            self.increase_gas_price()
            return False

    def send_message_exception_handler(self, e):
        self.logger.debug('send_message_exception_handler')
        try:
            if e.args[0]['message'] == 'replacement transaction underpriced':
                raise UnderpricedReplacementTransactionException() from e
        except (IndexError, KeyError, TypeError):
            pass

    def send_message(self, message):
        self.logger.debug('send_message')
        # nonce calulated without pending transactions to replace stuck transaction
        tx = {
            'from': self.sender_public_key,
            'nonce': self.web3.eth.getTransactionCount(self.sender_public_key),
            'gasPrice': self.gas_price
        }
        try:
            tx = self.contract.functions.send(message).buildTransaction(tx)
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.sender_private_key)
            tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            self.web3.eth.waitForTransactionReceipt(tx_hash, self.transaction_wait_time)
        except ValueError as e:
            self.send_message_exception_handler(e)
            raise

    def set_gas_price_strategy(self, strategy):
        self.logger.debug('set_gas_price_strategy')
        if strategy == 'fast':
            # 60 seconds per transaction
            self.message_visibility_timeout = 150
            self.web3.eth.setGasPriceStrategy(fast_gas_price_strategy)
        elif strategy == 'medium':
            # 5 minutes per transaction
            self.message_visibility_timeout = 600
            self.web3.eth.setGasPriceStrategy(medium_gas_price_strategy)
        # slow speed looks like it is too much, but i'll leave it here just in case
        elif strategy == 'slow':
            # 1 hour per transaction
            self.message_visibility_timeout = 5400
            self.web3.eth.setGasPriceStrategy(slow_gas_price_strategy)
        else:
            raise ValueError(f'Unknown gas price strategy:{repr(strategy)}')
        self.transaction_wait_time = self.message_visibility_timeout - 30
        self.logger.info('gas_price_strategy: %s', strategy)

    def refresh_gas_price(self):
        self.logger.debug('refresh_gas_price')
        self.logger.debug('transactions_count:%s', self.transactions_count)
        self.logger.debug('gas_price_refresh_rate:%s', self.gas_price_refresh_rate)
        if self.transactions_count % self.gas_price_refresh_rate == 0:
            self.logger.debug('refreshing gas price')
            self.update_gas_price()

    def update_gas_price(self):
        self.logger.debug('update_gas_price')
        self.gas_price = self.web3.eth.generateGasPrice()
        self.transactions_count = 1
        self.logger.debug('gas price updated:%s', self.gas_price)
        self.logger.debug('transactions_count reset')

    def increase_gas_price(self):
        self.logger.debug('increase_gas_price')
        new_gas_price = int(self.gas_price * self.gas_price_increase_factor)
        self.logger.info('Gas price increased, OLD: %s NEW: %s', self.gas_price, new_gas_price)
        self.gas_price = new_gas_price
