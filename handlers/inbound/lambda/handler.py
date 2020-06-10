import os


def handler_name(event, context):
    print("I'm a little function stub, short and stout")
    print("Here is my input %s" % (os.environ['CHANNEL_API_URL']))
    print("And here is my out %s" % (os.environ['MESSAGE_RX_API_URL']))
    return 'success'
