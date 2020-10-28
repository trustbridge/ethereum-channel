import time
from http import HTTPStatus
import urllib
import pytest
import requests

CHANNEL_API_GB_URL = 'http://tec-channel-api-gb:9091/'
CHANNEL_API_GB_SENDER = 'GB'
CHANNEL_API_GB_SENDER_REF = 'sender_ref:GB'

CHANNEL_API_AU_URL = 'http://tec-channel-api-au:9090/'
CHANNEL_API_AU_SENDER = 'AU'
CHANNEL_API_AU_SENDER_REF = 'sender_ref:AU'


class ChannelAPI:

    def __init__(self, base_url, sender, sender_ref):
        self.base_url = base_url
        self.sender = sender
        self.sender_ref = sender_ref

    def get_participants(self):
        url = urllib.parse.urljoin(self.base_url, 'participants')
        return requests.get(url)

    def get_message(self, id):
        url = urllib.parse.urljoin(self.base_url, f'messages/{id}')
        return requests.get(url)

    def get_topic_url(self, topic):
        return urllib.parse.urljoin(self.base_url, f'topic/{topic}')

    def get_topic(self, topic):
        url = urllib.parse.urljoin(self.base_url, f'topic/{topic}')
        return requests.get(url)

    def post_message(self, data):
        url = urllib.parse.urljoin(self.base_url, 'messages')
        return requests.post(url, json=data)

    def post_subscription_by_id(self, data):
        url = urllib.parse.urljoin(self.base_url, 'messages/subscriptions/by_id')
        return requests.post(url, data=data)

    def post_subscription_by_jurisdiction(self, data):
        url = urllib.parse.urljoin(self.base_url, 'messages/subscriptions/by_jurisdiction')
        return requests.post(url, data=data)


@pytest.fixture(scope='function')
def channel_api_gb():
    yield ChannelAPI(CHANNEL_API_GB_URL, CHANNEL_API_GB_SENDER, CHANNEL_API_GB_SENDER_REF)


@pytest.fixture(scope='function')
def channel_api_au():
    yield ChannelAPI(CHANNEL_API_AU_URL, CHANNEL_API_AU_SENDER, CHANNEL_API_AU_SENDER_REF)


class CallbackServer:

    def __init__(self, base_url=None):
        self.base_url = base_url

    def get_callback_record(self, index):
        url = urllib.parse.urljoin(self.base_url, f'callbacks/{index}')
        response = requests.get(url)
        if response.status_code == HTTPStatus.OK:
            return response.json()
        elif response.status_code == HTTPStatus.NOT_FOUND:
            return None
        else:
            raise Exception(f'Unexpected response:{response.status_code}')

    def __get_callback_records(self, id=None):
        url = urllib.parse.urljoin(self.base_url, 'callbacks')
        response = requests.get(url)
        if response.status_code == HTTPStatus.OK:
            records = response.json()
            if id is not None:
                return [record for record in records if record['id'] == id]
            else:
                return records
        else:
            raise Exception(f'Unexpected response:{response.status_code}')

    def get_callback_records(self, id=None, attemps=1, interval=1, delay=0):
        attemps = max(attemps, 1)
        for i in range(attemps):
            records = self.__get_callback_records(id=id)
            if records:
                return records
            else:
                time.sleep(interval)
        return []

    def clear_callback_records(self):
        url = urllib.parse.urljoin(self.base_url, 'callbacks')
        response = requests.delete(url)
        if response.status_code == HTTPStatus.OK:
            pass
        else:
            raise Exception(f'Unexpected response:{response.status_code}')

    def valid_callback_url(self, id):
        return urllib.parse.urljoin(self.base_url, f'callback/valid/{id}')

    def invalid_callback_url(self, id):
        return urllib.parse.urljoin(self.base_url, f'callback/invalid/{id}')


@pytest.fixture(scope='function')
def callback_server():
    callback_server = CallbackServer('http://tec-channel-api-callback-server:11001/')
    callback_server.clear_callback_records()
    yield callback_server
