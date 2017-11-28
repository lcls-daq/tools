#!/bin/bash

set -e

if [ ! -d tools ]; then
  echo "Please cd to the directory above build and tools before running this script"
  exit 1
fi

buildtype="unknown"
# check the jenkins node labels
for label in $NODE_LABELS
do
  if [ "$label" == "rhel7" ]; then
      tools/scripts/cleanbuild.sh  --no32
      buildtype="$label"
    elif [ "$label" == "rhel6" ]; then
      tools/scripts/cleanbuild.sh  --no32
      buildtype="$label"
    elif [ "$label" == "rhel5" ]; then
      tools/scripts/cleanbuild.sh
      buildtype="$label"
    fi
done

tools/scripts/tarcreate.sh pdsbuild-pdsapp-${buildtype}-${BUILD_NUMBER}-${SVN_REVISION}.tar.gz
