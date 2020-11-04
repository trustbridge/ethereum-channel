from http import HTTPStatus


def test(
    channel_api_gb,
    channel_api_au,
    callback_server
):

    """
    Testing channels participants lists.
    They must have each other on the participants list in order to communicate.
    """

    r = channel_api_au.get_participants()
    assert r.status_code == HTTPStatus.OK
    assert r.json() == [channel_api_gb.sender]
    r = channel_api_gb.get_participants()
    assert r.status_code == HTTPStatus.OK
    assert r.json() == [channel_api_au.sender]

    """
    Posting subscriptions to "jurisdiction.AU" and "jurisdiction.GB" topics.
    Currenly the only topics that cause notifications are "jurisdiction.<RECEIVER>" topics.
    All the subscriptions below are equivalent. The difference there is the way the topic
    is initially presented: unprefixed, prefixed, canonical url.
    """
    # PREFIXED TOPICS
    r = channel_api_au.post_subscription_by_jurisdiction({
        'hub.callback': callback_server.valid_callback_url('prefixed.jurisdiction.AU'),
        'hub.topic': 'AU',
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    r = channel_api_gb.post_subscription_by_jurisdiction({
        'hub.callback': callback_server.valid_callback_url('prefixed.jurisdiction.GB'),
        'hub.topic': 'GB',
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    # PREFIXED CANONICAL URL TOPICS
    r = channel_api_au.post_subscription_by_jurisdiction({
        'hub.callback': callback_server.valid_callback_url('url.jurisdiction.AU'),
        'hub.topic': channel_api_au.get_topic_url('AU'),
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    r = channel_api_gb.post_subscription_by_jurisdiction({
        'hub.callback': callback_server.valid_callback_url('url.jurisdiction.GB'),
        'hub.topic': channel_api_gb.get_topic_url('GB'),
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    # UNPREFIXED TOPICS
    r = channel_api_au.post_subscription_by_id({
        'hub.callback': callback_server.valid_callback_url('unprefixed.jurisdiction.AU'),
        'hub.topic': 'jurisdiction.AU',
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    r = channel_api_gb.post_subscription_by_id({
        'hub.callback': callback_server.valid_callback_url('unprefixed.jurisdiction.GB'),
        'hub.topic': 'jurisdiction.GB',
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    # UNPREFIXED TOPICS that should not receive notifications
    r = channel_api_gb.post_subscription_by_id({
        'hub.callback': callback_server.valid_callback_url('not.notify.AU'),
        'hub.topic': 'AU',
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    r = channel_api_gb.post_subscription_by_id({
        'hub.callback': callback_server.valid_callback_url('not.notify.GB'),
        'hub.topic': 'GB',
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    # shortcuts for the callback received message verifications
    def verify_callback_message_received(message, callback_id):
        records = callback_server.get_callback_records(
            id=callback_id,
            attemps=3,
            delay=1,
            interval=5
        )

        assert len(records) == 1
        assert records[0]['json'] == {'id': message['id']}

    def verify_callback_not_received_message(callback_id):
        assert not callback_server.get_callback_records(
            id=callback_id,
            attemps=3,
            delay=1,
            interval=5
        )

    def post_message(channel_api, message_data):
        r = channel_api.post_message(message_data)
        assert r.status_code == HTTPStatus.OK
        message = r.json()
        assert 'id' in message
        assert 'message' in message
        assert message['message'] == {
            **message_data,
            'sender': channel_api.sender,
            'sender_ref': channel_api.sender_ref
        }
        # testing that message added to a blockchain
        r = channel_api.get_message(message['id'])
        # testing that message recorded as expected
        assert r.status_code == HTTPStatus.OK
        assert r.json() == message, r.text
        return message

    """
    Posting the message from AU to GB
    Receivers(callback ids):
        1. prefixed.jurisdiction.GB
        2. url.jurisdiction.GB
        3. unprefixed.jurisdiction.GB
    Ignored by(callback ids):
        1. not.notify.GB
        2. not.notify.AU
        3. prefixed.jurisdiction.AU
        4. url.jurisdiction.AU
        5. unprefixed.jurisdiction.AU
    """

    # clearing callback server records to remove records of the previous callbacks
    callback_server.clear_callback_records()

    message = {
        "subject": "subject",
        "predicate": "predicate",
        "object": "hello world",
        "receiver": "GB"
    }

    message = post_message(channel_api_au, message)

    # verify expected receivers
    verify_callback_message_received(message, 'prefixed.jurisdiction.GB')
    verify_callback_message_received(message, 'url.jurisdiction.GB')
    verify_callback_message_received(message, 'unprefixed.jurisdiction.GB')
    # verify ignored receivers
    verify_callback_not_received_message('not.notify.GB')
    verify_callback_not_received_message('not.notify.AU')
    verify_callback_not_received_message('prefixed.jurisdiction.AU')
    verify_callback_not_received_message('url.jurisdiction.AU')
    verify_callback_not_received_message('unprefixed.jurisdiction.AU')

    """
    Posting the message from GB to AU
    Receivers(callback ids):
        1. prefixed.jurisdiction.AU
        2. url.jurisdiction.AU
        3. unprefixed.jurisdiction.AU
    Ignored by(callback ids):
        1. not.notify.GB
        2. not.notify.AU
        3. prefixed.jurisdiction.GB
        4. url.jurisdiction.GB
        5. unprefixed.jurisdiction.GB
    """

    # clearing callback server records to remove records of the previous callbacks
    callback_server.clear_callback_records()

    message = {
        "subject": "subject",
        "predicate": "predicate",
        "object": "hello world",
        "receiver": "AU"
    }

    message = post_message(channel_api_gb, message)

    # verify expected receivers
    verify_callback_message_received(message, 'prefixed.jurisdiction.AU')
    verify_callback_message_received(message, 'url.jurisdiction.AU')
    verify_callback_message_received(message, 'unprefixed.jurisdiction.AU')
    # verify ignored receivers
    verify_callback_not_received_message('not.notify.GB')
    verify_callback_not_received_message('not.notify.AU')
    verify_callback_not_received_message('prefixed.jurisdiction.GB')
    verify_callback_not_received_message('url.jurisdiction.GB')
    verify_callback_not_received_message('unprefixed.jurisdiction.GB')

    """
    Testing that deleted subscriptions will not receive notifications.
    There are 3 variants of subscription. Each supports unsubscribe mode.
    Unsubscribing one by one and testing that after all they will not receive any messages.
    """

    # clearing callback server records to remove records of the previous callbacks
    callback_server.clear_callback_records()

    # UNSUBSCRIBE FROM PREFIXED TOPIC
    r = channel_api_au.post_subscription_by_jurisdiction({
        'hub.callback': callback_server.valid_callback_url('prefixed.jurisdiction.AU'),
        'hub.topic': 'AU',
        'hub.lease_seconds': 3600,
        'hub.mode': 'unsubscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    message = {
        "subject": "subject",
        "predicate": "predicate",
        "object": "hello world",
        "receiver": "AU"
    }

    message = post_message(channel_api_gb, message)
    # verify expected receivers
    verify_callback_message_received(message, 'url.jurisdiction.AU')
    verify_callback_message_received(message, 'unprefixed.jurisdiction.AU')
    # verify ignored receivers
    verify_callback_not_received_message('prefixed.jurisdiction.AU')

    # clearing callback server records to remove records of the previous callbacks
    callback_server.clear_callback_records()

    # UNSUBSCRIBE FROM UNPREFIXED TOPIC
    r = channel_api_au.post_subscription_by_id({
        'hub.callback': callback_server.valid_callback_url('unprefixed.jurisdiction.AU'),
        'hub.topic': 'jurisdiction.AU',
        'hub.lease_seconds': 3600,
        'hub.mode': 'unsubscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    message = {
        "subject": "subject",
        "predicate": "predicate",
        "object": "hello world",
        "receiver": "AU"
    }

    message = post_message(channel_api_gb, message)
    # verify expected receivers
    verify_callback_message_received(message, 'url.jurisdiction.AU')
    # verify ignored receivers
    verify_callback_not_received_message('unprefixed.jurisdiction.AU')
    verify_callback_not_received_message('prefixed.jurisdiction.AU')

    # clearing callback server records to remove records of the previous callbacks
    callback_server.clear_callback_records()

    # UNSUBSCRIBE FROM PREFIXED CANONICAL URL TOPIC
    r = channel_api_au.post_subscription_by_jurisdiction({
        'hub.callback': callback_server.valid_callback_url('url.jurisdiction.AU'),
        'hub.topic': channel_api_au.get_topic_url('AU'),
        'hub.lease_seconds': 3600,
        'hub.mode': 'unsubscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    message = {
        "subject": "subject",
        "predicate": "predicate",
        "object": "hello world",
        "receiver": "AU"
    }

    message = post_message(channel_api_gb, message)
    # verify ignored receivers
    verify_callback_not_received_message('url.jurisdiction.AU')
    verify_callback_not_received_message('unprefixed.jurisdiction.AU')
    verify_callback_not_received_message('prefixed.jurisdiction.AU')
