#!/usr/bin/env bash

# WAITING FOR UNLOCK FILES(DEV ENV ONLY)
if [[ -d /tmp/unlock-file ]]; then
  REQUIRED_UNLOCK_FILES=($REQUIRED_UNLOCK_FILES)
  echo "Waiting for unlock files (${REQUIRED_UNLOCK_FILES[@]})"
  all_files_exist=0
  while [[ $all_files_exist -eq 0 ]]; do
    all_files_exist=1
    for filename in "${REQUIRED_UNLOCK_FILES[@]}"; do
      unlock_file=/tmp/unlock-file/$filename
      if [[ ! -e $unlock_file ]]; then
        all_files_exist=0
      fi
    done
    sleep 1
  done
fi
original_entrypoint_script=$1
shift
$original_entrypoint_script $@
