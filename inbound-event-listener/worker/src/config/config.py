import os
import json
from collections import Counter
import yaml
from . import schema


class Worker:

    class __Blockchain:
        def __init__(self, config_dict):
            self.URI = config_dict['URI']

    class __Contract:
        def __init__(self, config_dict):
            self.ABI = config_dict['ABI']
            self.Address = config_dict['Address']

    class __General:
        def __init__(self, config_dict):
            self.PollingInterval = config_dict['PollingInterval']
            self.ListenerBlocksLogDir = config_dict['ListenerBlocksLogDir']
            self.LoggerName = config_dict['LoggerName']

    def __init__(self, config_dict):
        self.Blockchain = self.__Blockchain(config_dict['Blockchain'])
        self.General = self.__General(config_dict['General'])
        self.Contract = self.__Contract(config_dict['Contract'])


class Listener:

    class __Event:
        def __init__(self, config_dict):
            self.Name = config_dict['Name']
            self.Filter = config_dict['Filter']

    def __init__(self, config_dict):
        self.Id = config_dict['Id']
        self.Event = self.__Event(config_dict['Event'])
        self.Receivers = config_dict['Receivers']


class Receiver:
    def __init__(self, config_dict):
        self.Id = config_dict['Id']


class LogReceiver(Receiver):
    pass


class SQSReceiver(Receiver):
    class __Config:
        def __init__(self, config_dict):
            self.Message = config_dict['Message']
            self.AWS = config_dict['AWS']

    def __init__(self, config_dict):
        super().__init__(config_dict)
        self.QueueUrl = config_dict['QueueUrl']
        self.Config = self.__Config(config_dict['Config'])


class Config:

    @staticmethod
    def from_file(filename):
        name, ext = os.path.splitext(filename)
        with open(filename, 'rt') as f:
            if ext in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif ext in ['.json']:
                data = json.load(f)
            else:
                raise ValueError(f'Unsupported config file extension "{ext}"')
        data = schema.Config().load(data)
        return Config(data)

    def __init__(self, config_dict):
        self.Worker = Worker(config_dict['Worker'])
        self.Receivers = []
        for receiver_config in config_dict['Receivers']:
            type = receiver_config['Type']
            if type == 'LOG':
                self.Receivers.append(LogReceiver(receiver_config))
            elif type == 'SQS':
                self.Receivers.append(SQSReceiver(receiver_config))
            else:  # pragma: no cover (extra protection)
                raise ValueError(f'Unknown Receiver type "{type}"')
        self.Listeners = [Listener(listener_config) for listener_config in config_dict['Listeners']]
        self.__validate()

    def __validate(self):
        receiver_ids = [r.Id for r in self.Receivers]
        listener_ids = [l.Id for l in self.Listeners]
        if receiver_id_duplicates := [k for k, v in Counter(receiver_ids).items() if v > 1]:
            raise ValueError(f'Reciver id duplicates found {receiver_id_duplicates}')
        if listener_id_duplicates := [k for k, v in Counter(listener_ids).items() if v > 1]:
            raise ValueError(f'Listener id duplicates found {listener_id_duplicates}')
        for listener in self.Listeners:
            for id in listener.Receivers:
                if id not in receiver_ids:
                    raise ValueError(f'Receiver "{id}" not found')
