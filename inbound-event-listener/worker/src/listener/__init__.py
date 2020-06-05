import os
from web3 import Web3
from src.loggers import logging


class Listener:

    @staticmethod
    def from_config_list(contract=None, receivers=None, config_list=None, global_config=None):
        return [Listener(contract, receivers, config, global_config) for config in config_list]

    def __load_from_block(self):
        try:
            with open(self.__from_block_filename, 'rt') as f:
                value = int(f.read())
                self.__logger.debug('from block=%s file loaded', value)
                return value
        except (ValueError, FileNotFoundError):
            return 0

    def __update_from_block(self, value):
        with open(self.__from_block_filename, 'wt+') as f:
            f.write(str(value))
        self.__logger.debug('from block updated=%s', self.__from_block)

    def __update_filter(self):
        config = self.__config
        contract = self.__contract
        from_block = self.__from_block
        default_filter_config = {'fromBlock': from_block, 'toBlock': 'latest'}
        filter_config = {**default_filter_config, **config.Event.Filter}
        # if we are replacing previous filter
        if self.__filter is not None:
            filter_config['fromBlock'] = self.__from_block
        self.__filter = contract.events[config.Event.Name].createFilter(**filter_config)
        self.__logger.debug('new filter=%s', filter_config)

    def __init__(self, contract=None, receivers=None, config=None, global_config=None):
        self.__logger = logging.getLogger(config.Id)

        self.__contract = contract
        self.__config = config
        self.__global_config = global_config
        self.__receivers = tuple(receivers[id] for id in config.Receivers)
        self.__from_block_filename = os.path.join(global_config.Worker.General.ListenerBlocksLogDir, config.Id)
        self.__from_block = self.__load_from_block()
        self.__filter = None
        self.__update_filter()

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

        new_from_block = self.__from_block
        event_received = False
        event_count = 0
        for event in self.__filter.get_all_entries():
            self.__logger.debug('event received')
            self.__logger.debug('event.blockNumber=%s', event.blockNumber)
            # update filter if initial "fromBlock" = "latest"
            event_received = True
            # DUPLICATES AVOIDANCE
            if event.blockNumber < new_from_block:
                self.__logger.debug('event was already seen, ignored.')
                continue
            # start new filter from the next block
            new_from_block = event.blockNumber + 1
            message = Web3.toJSON(event)
            event_count += 1
            for receiver in self.__receivers:
                receiver.send(message)
        if event_received:
            self.__logger.debug('events count=%s', event_count)
            self.__from_block = new_from_block
            self.__update_from_block(new_from_block)
            self.__update_filter()
