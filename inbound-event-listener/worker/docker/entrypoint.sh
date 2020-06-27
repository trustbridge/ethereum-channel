#!/bin/bash
set -e

echo "Container started"

# Allow for translating a env var into a local config file
if [[ -n "${CONFIG_FILE_VALUE}" ]]; then
    echo "Config file provided by env var. Writing to file..."
    echo "${CONFIG_FILE_VALUE}" > /tmp/config.json
    export CONFIG_FILE="/tmp/config.json"
fi

exec "$@"
