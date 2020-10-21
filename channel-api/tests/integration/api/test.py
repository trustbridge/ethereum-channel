"""
This test relies on the correct environment setup.
Setup must contain two deployed contracts that are interlinked as participants.
The sender(used in the test) contract is 'AU',
and the receiver(required by the sender to send messages) contract is 'GB'.
"""
import uuid
from http import HTTPStatus
import pytest


def test_post_get_message(client, app):
    message = {
        "subject": "subject",
        "predicate": "predicate",
        "object": "object",
        "receiver": "GB"
    }
    response = client.post('/messages', json=message)
    assert response.status_code == HTTPStatus.OK
    assert 'id' in response.json
    assert response.json['id']
    assert isinstance(response.json['id'], str)
    assert 'status' in response.json
    assert response.json['status'] == 'received'
    message = {
        **message,
        'sender': app.config.SENDER,
        'sender_ref': app.config.SENDER_REF
    }
    assert response.json['message'] == message
    message_id = response.json['id']

    response = client.get(f'/messages/{message_id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json == {
        'id': message_id,
        'message': message,
        'status': 'received'
    }

    message_id = uuid.uuid4().hex
    response = client.get(f'/messages/{message_id}')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json['errors'][0]['detail'] == f'Message {{id:"{message_id}"}} not found'


def test_get_participants(client):
    response = client.get('/participants')
    assert response.status_code == HTTPStatus.OK
    assert response.json == ['GB']


def test_get_topic(client):
    topics = [
        'a',
        'a.b'
        'a.b.c',
        'a.b.c.*'
    ]
    for topic in topics:
        response = client.get(f'/topic/{topic}')
        assert response.status_code == HTTPStatus.OK
        assert response.json == topic
    invalid_topics = [
        'a/b/c',
        'a.b.c*'
        ''
    ]
    for invalid_topic in invalid_topics:
        response = client.get(f'/topic/{invalid_topic}')
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url,topic,pattern',
    [
        ['/messages/subscriptions/by_id', 'a.b.c', 'a.b.c'],
        ['/messages/subscriptions/by_id', 'TOPIC_BASE_URLa.b.c', 'a.b.c'],
        ['/messages/subscriptions/by_jurisdiction', 'a.b.c', 'jurisdiction.a.b.c'],
    ]
)
def test_subscriptions(client, app, subscriptions_repo, callback_server, url, topic, pattern):
    topic = topic.replace('TOPIC_BASE_URL', f'{app.config.TOPIC_BASE_URL}/')
    subscription_callback = callback_server.valid_callback_url(1)
    data = {
        'hub.mode': 'subscribe',
        'hub.topic': topic,
        'hub.lease_seconds': 3600,
        'hub.callback': subscription_callback
    }
    response = client.post(url, data=data, mimetype='application/x-www-form-urlencoded')
    assert response.status_code == HTTPStatus.OK, response.json

    data['hub.mode'] = 'unsubscribe'
    response = client.post(url, data=data, mimetype='application/x-www-form-urlencoded')
    assert response.status_code == HTTPStatus.OK, response.json

    response = client.post(url, data=data, mimetype='application/x-www-form-urlencoded')
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json
