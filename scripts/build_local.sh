#!/bin/bash

set -e

if [ ! -d tools ]; then
    echo "Please cd to the directory above build and tools before running this script"
    exit 1
fi

buildtype="unknown"
if [[ `uname -r` == *el5* ]]; then
    tools/scripts/build.sh --clean --fail
    buildtype="rhel5"
elif [[ `uname -r` == *el6* ]]; then
    tools/scripts/build.sh --clean --fail --no32
    buildtype="rhel6"
elif [[ `uname -r` == *el7* ]]; then
    tools/scripts/build.sh --clean --fail --no32
    buildtype="rhel7"
elif [[ `uname -r` == *el9* ]]; then
    tools/scripts/build.sh --clean --fail --no32
    buildtype="rhel9"
fi

tag="${1}"
commit="$(git rev-parse --short HEAD)"
version="${1-$commit}"
build="${2-0}"
tarball="pdsbuild-pdsapp-${buildtype}-b${build}-${version}.tar.gz"

tools/scripts/tarcreate.sh "$tarball"
chmod 444 "$tarball"
