#!/bin/bash
#
CLEAN=false

function make_link()
{
  if [ ! -e $1/$2 ]; then
    ln -s $2-opt $1/$2
  fi
}

for i in "$@"
do
if [[ "$i" == "--clean" ]] ; then
  CLEAN=true
elif [[ "$i" == "--fail" ]] ; then
  set -e
  export FAILONERR=true
fi
done

x86_64_arch='unknown'
if [[ `uname -r` == *el5* ]]; then
  x86_64_arch='x86_64-linux'
elif [[ `uname -r` == *el6* ]]; then
  x86_64_arch='x86_64-rhel6'
elif [[ `uname -r` == *el7* ]]; then
  x86_64_arch='x86_64-rhel7'
fi

if [[ "$CLEAN" == true ]] ; then
  make ${x86_64_arch}-opt.clean
  make ${x86_64_arch}-dbg.clean
fi

make ${x86_64_arch}-opt
make ${x86_64_arch}-dbg

make_link build/ami/lib ${x86_64_arch}

