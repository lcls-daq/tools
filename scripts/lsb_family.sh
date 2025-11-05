#
# source this file from sh or bash to define LSB_FAMILY as rhel5, rhel6, or rt9 (linuxRT)
#

if [ "$LSB_FAMILY" != "" ];
then
	return
fi

HAS_LSB=`which lsb_release 2> /dev/null`
if [ ! $? ];
then
	# 
	# Use lsb_release to determine which linux distribution we're using
	# lsb_release is the standard cmd line tool for displaying release information
	# LSB is a standard from the Free Standards Group and stands for Linux Standard Base
	#
	# First, determine the release family
	# Use the -i option to get the distributor id
	LSB_DIST_ID=`LD_LIBRARY_PATH= lsb_release -i | cut -f2`

	# Check for rhel family: RedHatEnterpriseClient and RedHatEnterpriseServer
	LSB_FAMILY=`echo $LSB_DIST_ID | sed -e "s/RedHatEnterprise.*/rhel/"`

	# TODO: Add tests for Ubuntu, SUSE, Mint, etc.
	#? LSB_FAMILY=`echo $LSB_FAMILY | sed -e "s/SuSE.*/suse/"`
	#? LSB_FAMILY=`echo $LSB_FAMILY | sed -e "s/Ubuntu.*/ubu/"`
	#? LSB_FAMILY=`echo $LSB_FAMILY | sed -e "s/Mint.*/mint/"`

	# Get the primary release number
	# For example, if "lsb_release -r" reports 5.8, our primary release is 5
	LSB_REL=`LD_LIBRARY_PATH= lsb_release -r | cut -f2 | cut -d. -f1`
	# Append the release number
	# For example, rhel5
	LSB_FAMILY=`echo ${LSB_FAMILY}${LSB_REL}`
else
	# lsb_release not available
	# Probably linuxRT rt9 kernel
	KERNEL=`uname -r`
	RT9_KERNEL=`echo $KERNEL | fgrep -e "-rt9"`
	if [ ! -z "$RT9_KERNEL" ]; then
		LSB_FAMILY=rt9
	else
		if [   ! -z "`echo $KERNEL | fgrep -e ".el5."`" ]; then
			LSB_FAMILY=rhel5
		elif [ ! -z "`echo $KERNEL | fgrep -e ".el6."`" ]; then
			LSB_FAMILY=rhel6
		elif [ ! -z "`echo $KERNEL | fgrep -e ".el7."`" ]; then
			LSB_FAMILY=rhel7
        elif [ ! -z "`echo $KERNEL | fgrep -e ".el8."`" ]; then
            LSB_FAMILY=rhel8
        elif [ ! -z "`echo $KERNEL | fgrep -e ".el9_"`" ]; then
            LSB_FAMILY=rhel9
		fi
	fi
fi

# set the daq arch
if [ "$LSB_FAMILY" == "rhel9" ]; then
    DAQ_ARCH=x86_64-rhel9-opt
    PKG_ARCH=x86_64-rhel9-gcc114-opt
elif [ "$LSB_FAMILY" == "rhel8" ]; then
    DAQ_ARCH=x86_64-rhel7-opt
    PKG_ARCH=x86_64-rhel7-gcc48-opt
elif [ "$LSB_FAMILY" == "rhel7" ]; then
    DAQ_ARCH=x86_64-rhel7-opt
    PKG_ARCH=x86_64-rhel7-gcc48-opt
elif [ "$LSB_FAMILY" == "rhel6" ]; then
    DAQ_ARCH=x86_64-rhel6-opt
    PKG_ARCH=x86_64-rhel6-gcc44-opt
elif [ "$LSB_FAMILY" == "rhel5" ]; then
    DAQ_ARCH=x86_64-linux-opt
    PKG_ARCH=x86_64-rhel5-gcc41-opt
else
    DAQ_ARCH=x86_64-linux-opt
    PKG_ARCH=x86_64-rhel5-gcc41-opt
fi

kernel_family=$LSB_FAMILY
