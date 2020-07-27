# README

ECS truffle based contract deployment task

## How it works

**Key moments:**
1. The task uses S3 as truffle build artifacts storage.
1. The task loads a truffle project using volume. Volume mount path ```/deployer/contract```.

**Workflow**:
1. Copy the truffle project from ```/deployer/contract``` volume to ```/deployer/contract-deployment``` directory to not change an original project code. Safety measure.
1. Try to load existing truffle build artifacts zip from a specified S3 bucket and unzip it into ```/deployer/contract-deployment/build/contracts```.
1. Run standard truffle ```deploy``` operation.
1. Save the created/updated truffle build artifacts zip to the specified S3 bucket.
1. Run self-test to double-check integrity of the saved build artifacts zip.

Then contract ```address``` and ```abi``` can be extracted from build artifacts.
1. ```.networks[$network_id]["address"]```
1. ```.["abi"]```

## Task configuration
Task configured using environment variables

1. ```CONTAINER_MODE```.
  1. ```task``` run as ECS task.
  1. ```container``` run as development container.
1. ```CONTRACT_BUCKET_NAME```. The name of the bucket where the truffle project build artifacts will be stored.
1. ```CONTRACT_KEY_PREFIX```. Key prefix of the truffle project build artifact in the specified S3 bucket.
1. ```TRUFFLE_NETWORK_ID```: ID of an ethereum network to which contract will be deployed.
1. ```TRUFFLE_WALLET_PK```: Private key of a wallet that will be used that will be used to sign deployment transactions.
1. ```TRUFFLE_BLOCKCHAIN_ENDPOINT```: Blockhain endpoint url used to connect to a specific blockchain node. **Infura** URL can be used.
1. ```AWS_DEFAULT_REGION```
1. ```AWS_ACCESS_KEY_ID```
1. ```AWS_SECRET_ACCESS_KEY```
1. ```AWS_ENDPOINT_URL```
