#!/bin/bash

# check args
if [ $# -ne 2 ]; then
  echo "Usage: $0 <old_tag> <new_tag>"
  exit 1
fi

OLDTAG="${1}"
NEWTAG="${2}"

DAQ_DIRS="pds pdsapp timetool tools"
AMI_DIRS="ami tools"

git log "${OLDTAG}".."${NEW_TAG}"
for DIR in $DAQ_DIRS $AMI_DIRS
do
  if [ -d "$DIR" ]; then
    OLD_DIR="$PWD"
    cd -- "$DIR"
    git log "${OLDTAG}".."${NEW_TAG}"
    cd -- "$OLD_DIR"
  fi
done
