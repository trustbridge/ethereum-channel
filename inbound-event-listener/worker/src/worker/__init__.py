import os
import json
import time
from web3 import Web3
from src.contracts import EventEmitter
from src.receivers import Receiver
from src.listener import Listener


class Worker:

    BLOCKCHAIN_ENPOINT_URI = os.environ['BLOCKCHAIN_ENPOINT_URI']
    POLLING_INTERVAL = int(os.environ['POLLING_INTERVAL'])
    CONFIG_FILE = os.environ['CONFIG_FILE']

    def __establish_connection(self):
        return Web3(Web3.WebsocketProvider(self.BLOCKCHAIN_ENPOINT_URI))

    def __load_config(self):
        with open(self.CONFIG_FILE, 'rt') as f:
            return json.load(f)

    def __init__(self):
        web3 = self.__establish_connection()
        contract = EventEmitter(web3)
        config = self.__load_config()
        receivers = Receiver.mapping_from_list(config['Receivers'])
        self.listeners = Listener.from_config_list(web3, contract, receivers, config['Listeners'])

    def run(self):
        while True:
            for listener in self.listeners:
                listener.poll()
            time.sleep(self.POLLING_INTERVAL)
