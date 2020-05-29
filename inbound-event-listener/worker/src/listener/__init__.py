from web3 import Web3


class Listener:

    @staticmethod
    def from_config_list(web3=None, contract=None, receivers=None, config_list=None):
        return [Listener(web3, contract, receivers, config) for config in config_list]

    def __init__(self, web3=None, contract=None, receivers=None, config=None):
        event = config['Event']
        receiver_ids = config['Receivers']
        self.filter = contract.events[event['Name']].createFilter(**event['Filter'])
        self.receivers = []
        for id in receiver_ids:
            self.receivers.append(receivers[id])

    def poll(self):
        for event in self.filter.get_new_entries():
            message = Web3.toJSON(event)
            for receiver in self.receivers:
                receiver.send(message)
