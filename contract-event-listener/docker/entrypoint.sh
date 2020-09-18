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

# Allow for translating a env var into a local config file
if [[ -n "${CONFIG_FILE_VALUE}" ]]; then
    echo "Config file provided by env var. Writing to file..."
    echo "${CONFIG_FILE_VALUE}" > /tmp/config.json
    export CONFIG_FILE="/tmp/config.json"
fi

exec "$@"
