import boto3
from src import config


class Receiver:
    @staticmethod
    def from_config(config_obj):
        if isinstance(config_obj, config.SQSReceiver):
            return SQSReceiver(config_obj)
        elif isinstance(config_obj, config.LogReceiver):
            return LogReceiver(config_obj)

    @staticmethod
    def mapping_from_list(receiver_list):
        mapping = dict()
        for config_obj in receiver_list:
            mapping[config_obj.Id] = Receiver.from_config(config_obj)
        return mapping


class SQSReceiver(Receiver):
    def __init__(self, config_obj):
        self.config = config_obj
        self.__queue = boto3.resource('sqs', **config_obj.Service).Queue(config_obj.QueueUrl)

    def send(self, message):
        kwargs = {**self.config.Message, 'MessageBody': message}
        self.queue.send_message(**kwargs)


class LogReceiver(Receiver):
    def __init__(self, config_obj):
        self.config = config_obj

    def send(self, message):
        print(f'[{self.config.Id}]:{message}')
