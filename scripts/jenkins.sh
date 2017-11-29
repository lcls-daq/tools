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
      tools/scripts/build.sh --clean --fail --no32
      buildtype="$label"
    elif [ "$label" == "rhel6" ]; then
      tools/scripts/build.sh --clean --fail --no32
      buildtype="$label"
    elif [ "$label" == "rhel5" ]; then
      tools/scripts/build.sh --clean --fail
      buildtype="$label"
    fi
done

tag="${1}"
version="${1-$GIT_COMMIT}"
tarball="pdsbuild-pdsapp-${buildtype}-b${BUILD_NUMBER}-${version}.tar.gz"

tools/scripts/tarcreate.sh "$tarball"
chmod 444 "$tarball"
if [ -z "$tag" ]; then
  mv "$tarball" /reg/g/pcds/dist/pds/ci-artifacts/
else
  mv "$tarball" /reg/g/pcds/dist/pds/ci-artifacts/tags/
  echo "$tag" > /reg/g/pcds/dist/pds/ci-artifacts/tags/new_tag
fi
