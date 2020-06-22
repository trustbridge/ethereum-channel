import boto3
from src import config
from src.loggers import logging


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
        self.__logger = logging.getLogger(self.config.Id)
        self.__queue = boto3.resource('sqs', **config_obj.Config.AWS).Queue(config_obj.QueueUrl)

    def send(self, message):
        kwargs = {**self.config.Config.Message, 'MessageBody': message}
        self.__logger.debug('Sending the message to %s', self.config.QueueUrl)
        self.__logger.debug(message)
        self.__queue.send_message(**kwargs)
        self.__logger.debug('Message sent')


class LogReceiver(Receiver):
    def __init__(self, config_obj):
        self.config = config_obj
        self.__logger = logging.getLogger(self.config.Id)

    def send(self, message):
        self.__logger.info(message)
