#!/usr/bin/env bash

sleep $SLEEP

set -euo pipefail

case "${CONTAINER_MODE,,}" in
  task)
    cd /deployer
    bash scripts/deploy.sh
    ;;
  container)
    echo "Container started"
    tail -f /dev/null
    ;;
  *)
    echo "No mode specified" && exit 1
esac
