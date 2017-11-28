#!/bin/bash

set -e

if [ ! -d tools ]; then
  echo "Please cd to the directory above build and tools before running this script"
  exit 1
fi

# check the jenkins node labels
for label in $NODE_LABELS
do
  if [ "$label" == "rhel7" ]; then
      tools/scripts/cleanbuild.sh  --no32
    elif [ "$label" == "rhel6" ]; then
      tools/scripts/cleanbuild.sh  --no32
    elif [ "$label" == "rhel5" ]; then
      tools/scripts/cleanbuild.sh
    fi
done
