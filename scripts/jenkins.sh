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

version="${1-$GIT_COMMIT}"
tarball="pdsbuild-pdsapp-${buildtype}-${BUILD_NUMBER}-${version}.tar.gz"

tools/scripts/tarcreate.sh "$tarball"
chmod 444 "$tarball"
mv "$tarball" /reg/g/pcds/dist/pds/ci-artifacts/
