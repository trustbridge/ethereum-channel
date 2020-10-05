def test(empty_queue, MessageSent, MessageReceived):
    queue = empty_queue('notifications-dev')
    MessageSent('AU', 'Hi')
    MessageReceived('AU', 'Hello')
