from src.worker import Worker


def test(emitEvent, get_sqs_msgs):
    worker = Worker()
    emitEvent(1, 'HelloWorld')
    worker.poll()
    message = get_sqs_msgs(0)
    assert message
