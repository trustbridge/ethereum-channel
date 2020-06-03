import os
import time
from web3 import Web3
from src.contract import Contract
from src.receivers import Receiver
from src.listener import Listener
from src.config import Config


class Worker:

    def __init__(self):
        config = Config.from_file(os.environ['CONFIG_FILE'])
        self.config = config
        web3 = Web3(Web3.WebsocketProvider(config.Worker.Blockchain.URI))
        contract = Contract(web3, config.Worker.Contract.Address, config.Worker.Contract.ABI)
        receivers = Receiver.mapping_from_list(config.Receivers)
        self.listeners = Listener.from_config_list(web3, contract, receivers, config.Listeners)

    def poll(self):
        for listener in self.listeners:
            listener.poll()

    def run(self):
        while True:
            self.poll()
            time.sleep(self.config.Worker.General.PollingInterval)
