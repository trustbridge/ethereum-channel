import os
import yaml
import time
from web3 import Web3
from src.contracts import EventEmitter
from src.receivers import Receiver
from src.listener import Listener
from src.config import Config


class Worker:

    def __establish_connection(self, uri):
        return Web3(Web3.WebsocketProvider(uri))

    def __load_config(self, filename):
        with open(filename, 'rt') as f:
            return Config().load(yaml.safe_load(f))

    def __init__(self):
        config_filename = os.environ['CONFIG_FILE']
        config = self.__load_config(config_filename)
        print(config)
        uri = config['Worker']['Blockhain']['URI']
        web3 = self.__establish_connection(uri)
        contract = EventEmitter(web3)
        receivers = Receiver.mapping_from_list(config['Receivers'])
        self.polling_interval = config['Worker']['General']['PollingInterval']
        self.listeners = Listener.from_config_list(web3, contract, receivers, config['Listeners'])

    def run(self):
        while True:
            for listener in self.listeners:
                listener.poll()
            time.sleep(self.polling_interval)
