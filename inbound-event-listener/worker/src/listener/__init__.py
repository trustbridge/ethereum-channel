import os
import copy
from web3 import Web3
from src.loggers import logging


class Listener:

    @staticmethod
    def from_config_list(web3=None, contract=None, receivers=None, config_list=None, blocks_log_dir=None):
        return [Listener(web3, contract, receivers, config, blocks_log_dir) for config in config_list]

    def __load_last_seen_block(self):
        self.logger.debug('Trying to load last seen block from %s...', self.last_seen_block_file)
        try:
            with open(self.last_seen_block_file, 'rt') as f:
                last_seen_block = int(f.read())
                self.logger.debug('File found. Last seen block = %s', last_seen_block)
                return last_seen_block
        except FileNotFoundError:
            self.logger.debug('File not found, using default last seen block value = 0')
            return 0

    def __update_last_seen_block(self, block_number):
        if self.last_seen_block == block_number:
            return
        self.last_seen_block = block_number
        with open(self.last_seen_block_file, 'wt') as f:
            f.write(str(block_number))
        self.logger.debug('%s updated [%s]', self.last_seen_block_file, self.last_seen_block)

    def __send_events_to_receivers(self, events):
        # new last seen block will be recorded only after the first successful poll
        new_last_seen_block = self.last_seen_block
        events_count = 0
        for event in events:
            events_count += 1
            block_number = event['blockNumber']
            if new_last_seen_block < block_number:
                new_last_seen_block = block_number
            message = Web3.toJSON(event)
            for receiver in self.receivers:
                receiver.send(message)
        if events_count > 0:
            self.logger.debug('Received %s event(s)', events_count)
        self.__update_last_seen_block(new_last_seen_block)

    def __create_receivers(self, config, receivers):
        self.receivers = []
        for id in config.Receivers:
            self.receivers.append(receivers[id])

    def __create_filter_configs(self, config, contract, blocks_log_dir):
        # if last seen block is None start from the first block
        last_seen_block = self.__load_last_seen_block()
        default_filter_config = {'fromBlock': last_seen_block}
        # config.Event.Filter can override last seen block
        filter_config = {**default_filter_config, **config.Event.Filter}
        synchronized = filter_config['fromBlock'] == 'latest'
        # do not synchronize missed events if config specfies 'latest' as the fromBlocks
        if not synchronized:
            synchronization_filter_config = copy.deepcopy(filter_config)
            if synchronization_filter_config['fromBlock'] > 0:
                # to not catch already received events
                synchronization_filter_config['fromBlock'] += 1
        else:
            synchronization_filter_config = None

        self.last_seen_block = last_seen_block
        self.filter_config = filter_config
        self.synchronization_filter_config = synchronization_filter_config
        self.logger.debug('Filter config %s', filter_config)
        self.logger.debug('Synchronization filter config %s', synchronization_filter_config)

    def __create_filters(self, config, contract):
        self.filter = contract.events[config.Event.Name].createFilter(**self.filter_config)
        if self.synchronization_filter_config:
            self.synchronization_filter = contract.events[config.Event.Name].createFilter(
                **self.synchronization_filter_config
            )
            self.logger.debug('Synchronization filter created')
        else:
            self.logger.debug('Synchronization filter creation not required')
            self.synchronization_filter = None

    def __init__(self, web3=None, contract=None, receivers=None, config=None, blocks_log_dir=None):
        self.logger = logging.getLogger(config.Id)
        self.last_seen_block_file = os.path.join(blocks_log_dir, config.Id)
        self.__create_receivers(config, receivers)
        self.__create_filter_configs(config, contract, blocks_log_dir)
        self.__create_filters(config, contract)

    def synchronize(self):
        if not self.synchronization_filter:
            self.logger.debug('Synchronization not required')
            return
        self.logger.debug('Starting synchronization of missed events[blockNumber=%s]...', self.last_seen_block)
        self.__send_events_to_receivers(self.synchronization_filter.get_all_entries())
        self.logger.debug('Synchronization completed[blockNumber=%s]', self.last_seen_block)

    def poll(self):
        self.__send_events_to_receivers(self.filter.get_new_entries())
