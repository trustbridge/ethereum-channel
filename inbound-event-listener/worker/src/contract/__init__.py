import json


def Contract(web3, address, abi):
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
