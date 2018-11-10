#!/reg/g/pcds/package/python-2.5.2/bin/python
#

import pycdb
from scanutil import *

def test(d,n,name):
    o = get_dict(d,name)
    set_dict(d,name,n)
    v = get_dict(d,name)

    if v==o:
        print name+' unchanged!'
    elif v==n:
        print name+' correctly changed'
    else:
        print name+' corrupted!'


if __name__ == "__main__":
    import sys

#    cdb = pycdb.Db('/reg/neh/home/weaver/configdb/std')
    cdb = pycdb.Db('/reg/neh/home/tookey/configdb/lab2')
    detectorValue = 0x3200
    typeIdValue = 0x10078
    key = 0x164
    xtc = cdb.get(key=key,src=detectorValue,typeid=typeIdValue)[0]
    print xtc
    epix = xtc.get(0)
#    print epix
    dump_dict(epix)

    test(epix,9,'evr.runDelay')
    test(epix,3,'elemCfg[3].asicMask')
    test(epix,1,'elemCfg[3].asics[3].RowStop')

    for i in range(3):
        xtc.set(epix, i)

    test(epix,3,'evr.runDelay')
    test(epix,9,'elemCfg[3].asicMask')


#    set_dict(epix,'quad.testDataMask',1)
#    test(epix['quad']['testDataMask'],0,1,'quad.testDataMask')

#    set_dict(epix,'quads[*].testDataMask',1)
#    for i in range(4):
#        test(epix['quads'][i]['testDataMask'],0,1,'quads[%d].testDataMask'%i)


