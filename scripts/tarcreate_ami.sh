#!/bin/bash
#

set -u
set -e

# require one parameter and no flags
if [[ $# -ne 1 || ${1:0:1} == '-' ]]; then
  echo "Usage: $0 <outfile>"
  exit 1
fi

# create the tar file
/bin/tar czvf $1 \
  --exclude=.svn --exclude=dep --exclude=obj --exclude='*.cc' --exclude=.buildbot-sourcedata \
  build ami/event/CspadTemp.hh ami/data tools
