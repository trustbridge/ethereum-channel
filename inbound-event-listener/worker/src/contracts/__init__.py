import json


def EventEmitter(web3, address):
    with open('/contracts/eventEmitter/build/contracts/EventEmitter.json', 'rt') as f:
        abi = json.load(f)['abi']
    return web3.eth.contract(address=address, abi=abi)
