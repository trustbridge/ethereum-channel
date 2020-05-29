import os
import json


def __GenericContract(web3, address, abi):
    try:
        with open(address, 'rt') as f:
            address = f.read()
    except FileNotFoundError:
        pass
    try:
        with open(abi, 'rt') as f:
            abi = json.load(f)['abi']
    except FileNotFoundError:
        abi = json.loads(abi)['abi']
    return web3.eth.contract(address=address, abi=abi)


def EventEmitter(web3, address=None, abi=None):
    return __GenericContract(
        web3,
        os.environ.get('EVENT_EMITTER_ADDRESS', address),
        os.environ.get('EVENT_EMITTER_ABI_JSON', abi)
    )
