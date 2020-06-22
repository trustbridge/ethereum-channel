import json


def Contract(web3, address, abi):
    with open(address, 'rt') as f:
        address = f.read()
    with open(abi, 'rt') as f:
        abi = json.load(f)['abi']
    return web3.eth.contract(address=address, abi=abi)
