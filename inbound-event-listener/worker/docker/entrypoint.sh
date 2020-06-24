#!/usr/bin/env bash

sleep $SLEEP

set -euo pipefail

case "${CONTAINER_MODE,,}" in
  worker)
    cd /worker
    make run
    ;;
  worker-debug)
    cd /worker
    make run-debug
    ;;
  container)
    echo "Container started"
    tail -f /dev/null
    ;;
  *)
    echo "No mode specified" && exit 1
esac
