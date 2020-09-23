from src.config import Config



CONFIG_DICT = {
    "Receivers": [
        {
            "Id": "LogReceiver-1",
            "Type": "LOG"
        },
        {
            "Id": "LogReceiver-2",
            "Type": "LOG"
        },
        {
            "Id": "SQSReceiver-1",
            "Type": "SQS",
            "QueueUrl": "http://aws/queue-1",
            "Config": {
                "AWS": {
                    "region_name": "us-east-1"
                }
            }
        },
        {
            "Id": "SQSReceiver-2",
            "Type": "SQS",
            "QueueUrl": "http://aws/queue-2",
            "Config": {
                "AWS": {
                    "region_name": "us-east-2"
                }
            }
        }
    ],
    "Listeners": [
        {
            "Id": "EventListener-1",
            "Event": {
                "Name": "Event-1",
                "Filter": {
                    "fromBlock": "latest"
                }
            },
            "Receivers": [
                "LogReceiver-1",
                "SQSReceiver-1"
            ]
        },
        {
            "Id": "EventListener-2",
            "Event": {
                "Name": "Event-2"
            },
            "Receivers": [
                "LogReceiver-2",
                "SQSReceiver-2"
            ]
        }
    ],
    "Worker": {
        "Blockchain": {
            "URI": "ws://blockchain.com"
        },
        "General": {
            "PollingInterval": 5,
            "LoggerName": "Worker",
            "ListenerBlocksLogDir": "/tmp/blocks-log"
        },
        "Contract": {
            "ABI": "/tmp/contract/abi.json",
            "Address": "/tmp/contract/address.address"
        }
    }
}


def test_config_parsing():
    Config(CONFIG_DICT)
