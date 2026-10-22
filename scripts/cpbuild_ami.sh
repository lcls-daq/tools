#!/bin/csh
#
#  Copy libraries, binaries, and include files
#
if ($# < 1) exit

# Check if we are on cds or sdf
if ( -d /cds/group/pcds/dist/pds ); then
    setenv AMIBASE /cds/group/pcds/dist/pds
else
    setenv AMIBASE /sdf/group/lcls/ds/daq
endif

setenv AMIREL ${AMIBASE}/ami-$1
mkdir -p ${AMIREL}
mkdir -p ${AMIREL}/ami

#  Copy libraries and binaries
rsync -rlpogtSP --exclude={dep,obj,pds,pdsapp} build ${AMIREL}/.

#  Copy the header files
rsync -rlpogtSP --exclude={Makefile,.svn,\*.cc,\*.mk} ami/data ${AMIREL}/ami/.
mkdir -p ${AMIREL}/ami/event
rsync -rlpogtSP ami/event/CspadTemp.hh ${AMIREL}/ami/event/.

# Create soft link in DAQREL directory
cd ${AMIBASE}
if ( -e ${AMIBASE}/ami-current ) then
    rm -f ${AMIBASE}/ami-current
endif
ln -sf ./ami-$1 ami-current
chmod g+w ami-current
cd -
