#!/usr/bin/env bash

set -o errexit

cd /deployer

function usage(){
  cat <<END
USAGE:
  -s[str] - sleep before starting execution, uses sleep command argument format
  -e[str] - start a contract(external) script, value is a path to the script inside the contract directory
  -c[flag] - prevent this script from exiting after completion, usefull for docker debugging
  -d[flag] - start deployment procedure
END
}

while getopts ":s:e:dch" opt; do
  case ${opt} in
    c )
      CONTINUE=1
      ;;
    s ) # process option h
      SLEEP="$OPTARG"
      ;;
    d ) # process option t
      DEPLOY=1
      ;;
    e ) # process option t
      EXTERNAL_SCRIPTS+=("$OPTARG")
      ;;
    h )
      HELP=1
      ;;
    \? )
      HELP=1
      ;;
  esac
done
if [[ -n "$HELP" ]]; then
  usage;
  exit 1
fi
if [[ -n "$SLEEP" ]]; then
  echo "Sleep $SLEEP"
  sleep "$SLEEP"
fi
if [[ -n "$DEPLOY" ]]; then
  bash scripts/deploy.sh
fi
for SCRIPT in "${EXTERNAL_SCRIPTS[@]}"; do
  bash scripts/exec-external.sh "$SCRIPT"
done

# unlocking services that are waiting for the contract initialization
# replace all slashes with dashes
UNLOCK_FILE_NAME="$(echo $CONTRACT_KEY_PREFIX |  sed -e 's/\//-/g')"
if [ -d /tmp/unlock-file ]; then
  echo "Unlock file /tmp/unlock-file/$UNLOCK_FILE_NAME created"
  touch /tmp/unlock-file/$UNLOCK_FILE_NAME
fi

if [[ -n "$CONTINUE" ]]; then
  echo "Waiting forever..."
  tail -f /dev/null
fi
