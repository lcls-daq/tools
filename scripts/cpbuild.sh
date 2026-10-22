#!/bin/csh
#
#  Copy libraries, binaries, and include files
#
if ($# < 1) exit

# Check if we are on cds or sdf
if ( -d /cds/group/pcds/dist/pds ); then
    setenv DAQBASE /cds/group/pcds/dist/pds
else
    setenv DAQBASE /sdf/group/lcls/ds/daq
endif

setenv DAQREL ${DAQBASE}/$1
mkdir -p ${DAQREL}
#  Copy libraries and binaries
rsync -rlpogtSP --exclude={dep,obj} build ${DAQREL}/.

#  Copy the header files
mkdir -p ${DAQREL}/build/timetool/service
rsync -rlpogtSP --exclude={Makefile,.svn,\*.cc,\*.mk} timetool/service ${DAQREL}/build/timetool/.

#  Copy tools
rsync -rlpogtSP --exclude={CVS} tools ${DAQREL}/.

if ( -e build/ami ) then
    mkdir -p ${DAQREL}/ami/event
    rsync -rlpogtSP --exclude={Makefile,.svn,CVS,\*.cc,\*.mk,\*\~} ami/data ${DAQREL}/ami/.
    rsync -rlpogtSP ami/event/CspadTemp.hh ${DAQREL}/ami/event/.
endif

# Create soft link in DAQREL directory
cd ${DAQBASE}
if ( -e ${DAQBASE}/current ) then
    rm -f ${DAQBASE}/current
endif
ln -s ./$1 current
cd -
