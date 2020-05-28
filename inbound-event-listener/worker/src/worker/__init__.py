import os
import time
from web3 import Web3
from src.contracts import EventEmitter


def run():
    web3 = Web3(Web3.WebsocketProvider(os.environ.get('BLOCKCHAIN_ENPOINT_URI')))
    contract = EventEmitter(web3, "0x254dffcd3277C0b1660F6d42EFbB754edaBAbC2B")
    event_filter = contract.events.EventOne.createFilter(fromBlock='lastest')
    while True:
        events = event_filter.get_new_entries()
        for event in events:
            print(event)
        time.sleep(5)
