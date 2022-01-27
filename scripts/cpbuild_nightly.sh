#!/bin/bash
#
#  Copy libraries, binaries, and include files of latest buildbot release
#  to standard DAQ release area
#

function usage()
{
    echo -e "\nCopy the latest buildbot release to the PCDS release area and set current link(s)."
    echo -e "If the release name is preceded by 'ami-', then the lates AMI release is copied."
    echo -e "\nUsage:\n$0 <DAQ/AMI release> \n" 
}


if [ $# -lt 1 ]; then
    echo "ERROR:  Please provide DAQ/AMI release name"
    usage;
    exit 0;
fi

# exit immediately if a command exits with a non-zero status
set -e

# make sure the umask normal
umask 022

if [[ $1 == "ami-"* ]]; then
    RELTYP="ami"
else
    RELTYP="pdsapp"
fi

DAQREL="/reg/g/pcds/dist/pds/$1"
OLDREL="/reg/g/pcds/dist/pds/${1}_old"
BOT="/reg/g/pcds/dist/pds/ci-artifacts"

# delete old release
if [ -d "${OLDREL}" ]; then
  rm -rf $OLDREL
fi
# move existing to release to old
if [ -d "${DAQREL}" ]; then
  mv $DAQREL $OLDREL
fi

mkdir -p ${DAQREL}
CWD=`pwd`
cd $DAQREL


#  Copy rhel5 libraries and binaries
DAQBOT=$(ls -t -1 $BOT/pdsbuild-${RELTYP}-rhel5-* || echo)
for i in ${DAQBOT[@]}; do DAQBOT="$i"; break; done
if [ ! -z $DAQBOT ]; then
    echo "Copying $DAQBOT to $DAQREL"
    cp -rf $DAQBOT $DAQREL
    /bin/tar -xzf $DAQREL/*rhel5*.tar.gz
    rm -f $DAQREL/*rhel5*.tar.gz
fi

#  Copy rhel6 libraries and binaries
DAQBOT=$(ls -t -1 $BOT/pdsbuild-${RELTYP}-rhel6-* || echo)
for i in ${DAQBOT[@]}; do DAQBOT="$i"; break; done
if [ ! -z $DAQBOT ]; then
    echo "Copying $DAQBOT to $DAQREL"
    cp -rf $DAQBOT $DAQREL
    /bin/tar -xzf $DAQREL/*rhel6*.tar.gz
    rm -f $DAQREL/*rhel6*.tar.gz
fi

#  Copy rhel7 libraries and binaries
DAQBOT=$(ls -t -1 $BOT/pdsbuild-${RELTYP}-rhel7-* || echo)
for i in ${DAQBOT[@]}; do DAQBOT="$i"; break; done
if [ ! -z $DAQBOT ]; then
    echo "Copying $DAQBOT to $DAQREL"
    cp -rf $DAQBOT $DAQREL
    /bin/tar -xzf $DAQREL/*rhel7*.tar.gz
    rm -f $DAQREL/*rhel7*.tar.gz
fi

find $BOT -mindepth 1 -type f -name '*.tar.gz' -mtime +10 -delete

cd $CWD
