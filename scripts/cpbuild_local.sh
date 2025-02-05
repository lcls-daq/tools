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
    CURRENT="ami-current"
else
    RELTYP="pdsapp"
    CURRENT="current"
fi

DAQREL="/cds/group/pcds/dist/pds/$1"
mkdir -p ${DAQREL}
CWD=`pwd`
cd $DAQREL

#  Copy rhel5 libraries and binaries
DAQBOT=$(ls -t -1 $CWD/pdsbuild-${RELTYP}-rhel5-*-${1}* || echo)
for i in ${DAQBOT[@]}; do DAQBOT="$i"; break; done
if [ ! -z $DAQBOT ]; then
    echo "Copying $DAQBOT to $DAQREL"
    cp -rf $DAQBOT $DAQREL
    /bin/tar -xzf $DAQREL/*rhel5*.tar.gz
    rm -f $DAQREL/*rhel5*.tar.gz
fi

#  Copy rhel6 libraries and binaries
DAQBOT=$(ls -t -1 $CWD/pdsbuild-${RELTYP}-rhel6-*-${1}* || echo)
for i in ${DAQBOT[@]}; do DAQBOT="$i"; break; done
if [ ! -z $DAQBOT ]; then
    echo "Copying $DAQBOT to $DAQREL"
    cp -rf $DAQBOT $DAQREL
    /bin/tar -xzf $DAQREL/*rhel6*.tar.gz
    rm -f $DAQREL/*rhel6*.tar.gz
fi

#  Copy rhel7 libraries and binaries
DAQBOT=$(ls -t -1 $CWD/pdsbuild-${RELTYP}-rhel7-*-${1}* || echo)
for i in ${DAQBOT[@]}; do DAQBOT="$i"; break; done
if [ ! -z $DAQBOT ]; then
    echo "Copying $DAQBOT to $DAQREL"
    cp -rf $DAQBOT $DAQREL
    /bin/tar -xzf $DAQREL/*rhel7*.tar.gz
    rm -f $DAQREL/*rhel7*.tar.gz
fi

#  Copy rhel9 libraries and binaries
DAQBOT=$(ls -t -1 $CWD/pdsbuild-${RELTYP}-rhel9-*-${1}* || echo)
for i in ${DAQBOT[@]}; do DAQBOT="$i"; break; done
if [ ! -z $DAQBOT ]; then
    echo "Copying $DAQBOT to $DAQREL"
    cp -rf $DAQBOT $DAQREL
    /bin/tar -xzf $DAQREL/*rhel9*.tar.gz
    rm -f $DAQREL/*rhel9*.tar.gz
fi

# Create soft link in DAQREL directory
cd /reg/g/pcds/dist/pds
if [ -e /reg/g/pcds/dist/pds/${CURRENT} ]; then
    rm -f /reg/g/pcds/dist/pds/${CURRENT}
fi
ln -s ./$1 ${CURRENT}

cd $CWD
