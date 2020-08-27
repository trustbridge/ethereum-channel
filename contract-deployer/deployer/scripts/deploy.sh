#!/usr/bin/env bash

set -euo pipefail

export NODE_PATH="$(npm root -g --quiet)"
DEPLOYER_DIR=/deployer
DEPLOYER_SCRIPTS_DIR=$DEPLOYER_DIR/scripts
CONTRACT_DEPLOYMENT_DIR=/tmp/contract-deployment
CONTRACT_DIR=/tmp/contract

cd $DEPLOYER_DIR
cp -r $CONTRACT_DIR $CONTRACT_DEPLOYMENT_DIR
cp $DEPLOYER_SCRIPTS_DIR/truffle-config.js $CONTRACT_DEPLOYMENT_DIR/truffle-config.js
(cd $CONTRACT_DEPLOYMENT_DIR && truffle exec $DEPLOYER_SCRIPTS_DIR/load-build-artifacts.js --network production | npx pino-pretty)
(cd $CONTRACT_DEPLOYMENT_DIR && truffle deploy --network production)
(cd $CONTRACT_DEPLOYMENT_DIR && truffle exec $DEPLOYER_SCRIPTS_DIR/save-build-artifacts.js --network production | npx pino-pretty)
(cd $CONTRACT_DEPLOYMENT_DIR && truffle exec $DEPLOYER_SCRIPTS_DIR/self-test.js --network production | npx pino-pretty)
