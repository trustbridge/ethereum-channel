#!/usr/bin/env bash

set -euo pipefail

case "${1,,}" in
  server)
    cd /channel-api
    python -m src.api
    ;;
  callback-server)
    cd /channel-api
    python -m tests.utils.servers.callback
    ;;
  container)
    echo "Container started"
    tail -f /dev/null
    ;;
  *)
    echo "No mode specified" && exit 1
esac
