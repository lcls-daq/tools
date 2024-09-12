#!/bin/bash
#
BUILD32=true
CLEAN=false

function make_link()
{
  if [ ! -e $1/$2 ]; then
    ln -s $2-opt $1/$2
  fi
}

for i in "$@"
do
if [[ "$i" == "--no32" ]] ; then
  BUILD32=false
elif [[ "$i" == "--clean" ]] ; then
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
  BUILD32=false
elif [[ `uname -r` == *el7* ]]; then
  x86_64_arch='x86_64-rhel7'
  BUILD32=false
elif [[ `uname -r` == *el9* ]]; then
  x86_64_arch='x86_64-rhel9'
  BUILD32=false
fi

if [[ "$CLEAN" == true ]] ; then
  if [[ "$BUILD32" == true ]] ; then
    make i386-linux-opt.clean
    make i386-linux-dbg.clean
  fi
  make ${x86_64_arch}-opt.clean
  make ${x86_64_arch}-dbg.clean
fi

if [[ "$BUILD32" == true ]] ; then
  make i386-linux-opt
  make i386-linux-dbg
fi

make ${x86_64_arch}-opt
make ${x86_64_arch}-dbg

make_link build/pds/lib ${x86_64_arch}
make_link build/pdsdata/lib ${x86_64_arch}
make_link build/pdsapp/lib ${x86_64_arch}
make_link build/pdsapp/bin ${x86_64_arch}

