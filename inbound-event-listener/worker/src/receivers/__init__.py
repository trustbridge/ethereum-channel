import boto3


class Receiver:
    @staticmethod
    def from_config(config):
        type = config['Type']
        if type == 'SQS':
            return SQSReceiver(config)
        elif type == 'LOG':
            return LogReceiver(config)

    @staticmethod
    def mapping_from_list(receiver_list):
        mapping = dict()
        for config in receiver_list:
            mapping[config['Id']] = Receiver.from_config(config)
        return mapping


class SQSReceiver(Receiver):
    def __init__(self, config):
        queue_url = config['QueueUrl']
        service_config = config.get('Service', {})
        self.__message_config = config.get('Message', {})
        self.__queue = boto3.resource('sqs', **service_config).Queue(queue_url)

    def send(self, message):
        kwargs = {**self.__message_config, 'MessageBody': message}
        self.queue.send_message(**kwargs)


class LogReceiver(Receiver):
    def __init__(self, config):
        self.id = config['Id']

    def send(self, message):
        print(f'[{self.id}]:{message}')
