#!/usr/bin/env bash

set -euo pipefail

cd /deployer
cp -r contract contract-deployment
cp scripts/truffle-config.js contract-deployment/truffle-config.js
(cd contract-deployment && npx truffle exec ../scripts/load-build-artifacts.js --network production | npx pino-pretty)
(cd contract-deployment && npx truffle deploy --network production)
(cd contract-deployment && npx truffle exec ../scripts/save-build-artifacts.js --network production | npx pino-pretty)
