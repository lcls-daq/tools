#!/reg/g/pcds/package/python-2.5.2/bin/python
#

import pycdb
from scanutil import *

def test(v,o,n,name):
    if v==o:
        print name+' unchanged!'
    elif v==n:
        print name+' correctly changed'
    else:
        print name+' corrupted!'
    print


if __name__ == "__main__":
    import sys

    cdb = pycdb.Db('/reg/neh/home/weaver/configdb/std')
    detectorValue = 0x3000
    typeIdValue = 0x10075
    key = 0xb3
    xtc = cdb.get(key=key,src=detectorValue,typeid=typeIdValue)[0]
    print xtc
    epix = xtc.get(0)
#    print epix
    dump_dict(epix)

    epix['evr']['runDelay'] = 100
    set_dict(epix,'evr.runDelay',9)
    test(epix['evr']['runDelay'],100,9,'evr.runDelay')

    set_dict(epix,'quads[1].testDataMask',1)
    
    test(epix['quads'][1]['testDataMask'],0,1,'quads[1].testDataMask')

    set_dict(epix,'quads[*].testDataMask',1)
    for i in range(4):
        test(epix['quads'][i]['testDataMask'],0,1,'quads[%d].testDataMask'%i)


