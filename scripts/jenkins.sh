#!/bin/bash

set -e

for label in $NODE_LABELS
do
  if [ "$label" == "rhel7" ]; then
      tools/scripts/build.sh  --no32
    elif [ "$label" == "rhel6" ]; then
      tools/scripts/build.sh  --no32
    elif [ "$label" == "rhel5" ]; then
      tools/scripts/build.sh
    fi
done
