# README

The project consists of several sub-projects:
1. ```Channel API```
1. ```Contract Event Listener```
1. ```Contract```
1. ```Contract Deployer```

Each of them has its own respective README, this README goal is to explain how the system works overall.

In order to the system to function properly it needs at least 2 channels, each channel must have:
1. ```Channel API```
1. ```Contract Event Listener```
1. Deployed ```ChannelNode``` contract
1. ```New Messages Observer``` processor
1. ```Callback Spreader``` processor
1. ```Callback Delivery``` processor

The proper minimal setup is defined in ```docker-compose.system.yml```, it consists of:
1. ```localstack``` - AWS services emulation
1. ```ganache``` - Ethereum blockchain emulation
1. ```channel-api-callback-server``` - WebSub callbacks emulation and test utility
1. ```deployer-participant-(au|gb)``` - deploys ```ChannelNode``` contract
1. ```channel-api-(au|gb)``` - REST API for ```ChannelNode``` contract
1. ```new-messages-observer-(au|gb)``` - WebSub new channel messages listener
1. ```callback-spreader-(au|gb)``` - prepares WebSub notification delivery jobs
1. ```callback-delivery-(au|gb)``` - delivers WebSub notifications to callbacks
1. ```contract-event-listener-(au|gb)``` - redirects ```ChannelNode``` events to ```new-messages-observer```

> **NOTE:**
>
> Compose files are generated using ```Makefile```, they can't be used separately. The reason behind this is the > inability to use **YAML anchors** with native ```docker-compose``` compose files merging.


#### System Workflow:
1. Deployers deploy two ```ChannelNode``` contracts, ```ChannelNodeAU``` and ```ChannelNodeGB```
1. ```ChannelNodeAU``` and ```ChannelNodeGB``` go through their pairing process.
1. ```Channel API AU``` and ```Channel API GB``` services start including:
  1. ```New Messages Observer```
  1. ```Callback Spreader```
  1. ```Callback Delivery```
  1. ```Contract Event Listener```
1. User ```AU``` posts a message to ```Channel API AU``` via ```POST /messages``` with ```receiver=GB```
1. ```Channel API AU``` sends message via ```ChannelNodeAU```
1. ```ChannelNodeGB``` fires ```MessageReceivedEvent```
1. ```Contract Event Listener GB``` picks that event, reformats it and sends to ```New Messages Observer GB```
1. ```New Message Observer GB``` filters the event by ```receiver==GB``` and passes it to ```Callback Spreader GB```
1. ```Callback Spreader GB``` creates notification jobs for each topic subscriber and passes them to ```Callback Delivery GB```
1.  ```Callback Delivery GB``` posts notifications to the subscriptions callbacks.

#### HOW TO RUN(Development):
1. ```make run-system```
1. ```make shell-<service-name>``` where ```service-name``` is any of:
  1. ```channel-api-au```
  1. ```channel-api-gb```
  1. ```contract-event-listener-au```
  1. ```contract-event-listener-gb```
  1. ```deployer-participant-au```
  1. ```deployer-participant-gb```
  1. ```system-tests```
  1. ```localstack```
  1. ```ganache-cli```

#### HOW TO RUN(Manual testing):
1. ```make run-system```
1. Use ```Channel API AU``` on ```localhost:9090```
1. Use ```Channel API GB``` on ```localhost:9091```

#### HOW TO RUN(Automated testing):
1. ```make run-system-test```
1. ```make run-channel-api-au-test```
1. ```make run-contract-event-listner-test```

#### HOW TO RUN(Channel API development environment):
1. ```make run-channel-api-au```
1. ```make shell-channel-api-au```

#### HOW TO RUN(Contract Event Listener development environment)
1. ```make run-contract-event-listener```
1. ```make shell-contract-event-listener```

> **NOTE:**
>
> Every project service except third parties has ```container``` mode in which it will hang forever, it's useful for docker development. The way this mode set may differ, but it's always set through docker-compose service ```command``` option.
