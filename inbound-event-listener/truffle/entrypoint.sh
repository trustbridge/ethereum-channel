#!/usr/bin/env bash

# wait until ganache started
sleep 5

cd /truffle/contracts/EventEmitter && truffle deploy

echo "Container started, waiting forever..."

tail -f /dev/null
