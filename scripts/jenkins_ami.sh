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
    if [ "$label" == "rocky9" ]; then
        tools/scripts/build_ami.sh --clean --fail
        buildtype="rhel9"
    elif [ "$label" == "rhel9" ]; then
        tools/scripts/build_ami.sh --clean --fail
        buildtype="$label"
    elif [ "$label" == "rhel7" ]; then
        tools/scripts/build_ami.sh --clean --fail
        buildtype="$label"
    elif [ "$label" == "rhel6" ]; then
        tools/scripts/build_ami.sh --clean --fail
        buildtype="$label"
    elif [ "$label" == "rhel5" ]; then
        tools/scripts/build_ami.sh --clean --fail
        buildtype="$label"
    fi
done

tag="${1}"
version="${1-$GIT_COMMIT}"
tarball="pdsbuild-ami-${buildtype}-b${BUILD_NUMBER}-${version}.tar.gz"

tools/scripts/tarcreate_ami.sh "$tarball"
chmod 444 "$tarball"
if [ -z "$tag" ]; then
    mv "$tarball" /reg/g/pcds/dist/pds/ci-artifacts/
else
    mv "$tarball" /reg/g/pcds/dist/pds/ci-artifacts/tags/
    echo "$tag" > /reg/g/pcds/dist/pds/ci-artifacts/tags/new_tag_ami
fi

