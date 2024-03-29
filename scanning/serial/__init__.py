#!/usr/bin/env python 
#portable serial port access with python
#this is a wrapper module for different platform implementations
#
# (C)2001-2002 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

VERSION = '2.4'

import sys

if sys.platform == 'cli':
    from .serialcli import *
else:
    import os
    #chose an implementation, depending on os
    if os.name == 'nt': #sys.platform == 'win32':
        from .serialwin32 import *
    elif os.name == 'posix':
        from .serialposix import *
    elif os.name == 'java':
        from .serialjava import *
    else:
        raise Exception("Sorry: no implementation for your platform ('%s') available" % os.name)

