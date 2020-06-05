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

## DEV ENV

**Requirements**:
1. Docker
1. Docker Compose
1. Make

**Usage:**
1. ``cd`` to Inbound Event Listener root dir
1. ```make run-fg``` to start the project
1. ```make shell-worker``` to shell into worker container
1. ```make run``` inside worker container shell to start worker
1. ```make shell-truffle-console``` to open truffle console
1. ```let emitter = await EventEmitter.deployed()``` inside truffle console, then ```emitter.emitEvent(1, "EventMessage")```. This will emit and event named ```EventOne```. In the worker shell you'll see output signalizing that event was sent to corresponding receiver.
