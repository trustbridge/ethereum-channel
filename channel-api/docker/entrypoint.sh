#!/usr/bin/env bash

set -euo pipefail

case "${1,,}" in
  server)
    cd /channel-api
    python3 -m src.api
    ;;
  container)
    echo "Container started"
    tail -f /dev/null
    ;;
  *)
    echo "No mode specified" && exit 1
esac
