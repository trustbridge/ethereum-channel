# Inbound Event Listener

## Short Description
A single-threaded worker that listens for ethereum blockchain contract events according to provided configuration.

The configuration contains 3 main sections:
1. Worker: configures main worker parameters:
  1. Contract - events of which will be listened to.
  1. General - worker execution parameters.
  1. Blockchain - blockchain connection parameters.
1. Receivers - configures receivers for the events. There are 2 types of receivers:
    1. Log Receiver - outputs event payload using logger provided, STDOUT or Sentry.
    1. SQS Receiver - sends event payload to the specified queue.
1. Listeners - configures listeners that listen for a specified event of the contract and then send it to receivers.


## Example config

```yaml
---
  Receivers: # List of receivers
    -
      Id: LogReceiver
      Type: LOG
    -
      Id: SQSReceiver # required
      Type: SQS # required
      QueueUrl: http://ec-iel-localstack:10001/queue/queue-1 # required
      Config:
        AWS: # optional, https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html
          region_name: us-east-1
          endpoint_url: http://ec-iel-localstack:10001
        Message: # optional, https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Queue.send_message
          DelaySeconds: 5
  Listeners: # List of listeners
    -
      Id: EventOneListener # required
      Event: # required
        Name: EventOne # required, name of a contract event
        Filter: # optional, https://web3py.readthedocs.io/en/stable/filters.html#event-log-filters
          fromBlock: latest # disable synchronization using last seen block file
      Receivers: # required
        - LogReceiver # receiver id
    -
      Id: EventTwoListener
      Event:
        Name: EventTwo
      Receivers:
        - SQSReceiver
  Worker: # Worker configuration
    Blockchain: # required
      URI: ws://ec-iel-ganache-cli:8585 # connection url
    General:
      PollingInterval: 5  # optional, event polling interval (default=5)
      ListenerBlocksLogDir: /worker/listener-blocks-log # required, directory where worker records last seen blocks for each listener separately
    Contract: # required
      ABI:  /contracts/EventEmitter/build/contracts/EventEmitter.json # contract abi file, abi must be under "abi" key
      Address: /contracts/EventEmitter/address/EventEmitter.address # must contain contract address, single line

```


## DEV ENV

**Requirements**:
1. Docker
1. Docker Compose
1. Make

**Usage:**
1. ``cd`` to Inbound Event Listener root dir
1. ```make run-fg``` to start the project
1. ```make shell-worker``` to shell into worker container
1. ```make run-debug``` inside worker container shell to start worker
1. ```make shell-truffle-console``` to open truffle console
1. ```let emitter = await EventEmitter.deployed()``` inside truffle console, then ```emitter.emitEvent(1, "EventMessage")```. This will emit and event named ```EventOne```. In the worker shell you'll see output signalizing that event was sent to corresponding receiver.
