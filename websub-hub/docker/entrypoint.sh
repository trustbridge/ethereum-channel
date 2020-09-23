#!/usr/bin/env bash


case "${1,,}" in
  server)
    cd /contract-event-listener
    make run-api
    ;;
  callback-delivery-processor)
    cd /contract-event-listener
    make run-callback-delivery-processor
    ;;
  callback-spreader-processor)
    cd /contract-event-listener
    make run-callback-spreader-processor
    ;;
  new-messages-observer-processor)
    cd /contract-event-listener
    make run-new-messages-observer-processor
    ;;
  container)
    echo "Container started"
    tail -f /dev/null
    ;;
  *)
    echo "No mode specified" && exit 1
esac
