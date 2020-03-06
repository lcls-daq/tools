#!/bin/env python
##!/reg/g/pcds/package/python-2.5.2/bin/python
#

from scanutil import *

if __name__ == "__main__":

    scan_parameter('Jungfrau','JungfrauConfig', 'gainMode', ['Normal', 'ForcedGain1', 'ForcedGain2'], 'GainMode')
