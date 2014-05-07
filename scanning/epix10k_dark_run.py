#!/reg/g/pcds/package/python-2.5.2/bin/python
#

import pydaq
import pycdb
import math
import serial
import pprint

from optparse import OptionParser

if __name__ == "__main__":
    import sys

    parser = OptionParser()
    parser.add_option("-a","--address",dest="host",default='localhost',
                      help="connect to DAQ at HOST", metavar="HOST")
    parser.add_option("-p","--platform",dest="platform",type="int",default=3,
                      help="connect to DAQ at PLATFORM", metavar="PLATFORM")
    parser.add_option("-D","--detector",dest="detector",type="string",default='NoDetector',
                      help="detector to scan, default NoDetector",metavar="DET")
    parser.add_option("-I","--detectorID",dest="detectorID",type="int",default=0,
                      help="detector ID  to scan, default 0",metavar="D_ID")
#    parser.add_option("-d","--device",dest="device",type="string",default='Epix10k',
#                      help="device to scan, default Epix10k",metavar="DEV")
    parser.add_option("-i","--deviceID",dest="deviceID",type="int",default=0,
                      help="device ID to scan, default 0",metavar="DEV_ID")
    parser.add_option("-t","--typeIdVersion",dest="typeIdVersion",type="int",default=1,
                      help="type ID Version in use, default 1",metavar="typeIdVersion")
    parser.add_option("-A","--dbalias",dest="dbalias",type="string",
                      help="data base key in use",metavar="DBALIAS")
    parser.add_option("-e","--events",dest="events",type="int",default=1000,
                      help="record N events/cycle", metavar="EVENTS")
    (options, args) = parser.parse_args()
    
    options.device = 'Epix10k'
    options.typeId = 'Epix10kConfig'
    
    print 'host', options.host
    print 'platform', options.platform
    print 'dbalias',options.dbalias
    print 'events', options.events
    print 'detector', options.detector
    print 'detectorID', options.detectorID
    print 'device', options.device
    print 'deviceID', options.deviceID

    steps = 4

# Connect to the daq system
    daq = pydaq.Control(options.host,options.platform)
    daq.connect()
#    print 'Partition is', daq.partition()
    detectors = daq.detectors()
    devices = daq.devices()
    types = daq.types()
#    print 'types are :\n', types

	

    found = [False, False, False]
    index = 0
    for member in detectors :
        if member == options.detector :
            detectorValue = (index << 24) | ((options.detectorID&0xff)<<16)
            found[0] = True
        index = index + 1
    index = 0
    for member in devices :
        if member == options.device :
            detectorValue = detectorValue | (index << 8) | (options.deviceID & 0xff)
            found[1] = True
        index = index + 1
    index = 0;
    for member in types :
        if member == options.typeId :
            typeIdValue = index | (options.typeIdVersion<<16);
            found[2] = True
        index = index + 1
    if found[0] and found[1] and found[2]:
        print "detector hex value",  hex(detectorValue)
        print 'typeId', hex(typeIdValue)
    else :
        if not found[0] :
            print "Detector", options.detector, "not found!"
        if not found[1] :
            print "Device", options.device, "not found!"
        if not found[2] :
            print "Type", options.typeId, "not found!"
        print "Exiting"
        exit()
#
#  First, get the current configuration key in use and set the value to be used
#

    cdb = pycdb.Db(daq.dbpath())
    key = daq.dbkey()
    alias = daq.dbalias()
    print 'Retrieved key '+hex(key)+' alias '+alias

#
#  Generate a new key with different epix and EVR configuration for each cycle
#
    if options.dbalias==None:
        newkey = cdb.clone(alias)
    else:
        newkey = cdb.clone(options.dbalias)
    
    print 'Generated key ',hex(newkey)
    print 'key',hex(key)
    print 'detectorValue',hex(detectorValue)
    print 'typeIdValue',hex(typeIdValue)
#    xtcSet = cdb.get(key=key)
#    print 'xtcSet members :\n'
#    for member in xtcSet :
#        for attr in dir(member) :
#            print getattr(member,attr)            
#    print 'Done printing xtcSet\n'
#    print "cdb.get opened\n", cdb.get(key=key)
    xtc = cdb.get(key=key,src=detectorValue,typeid=typeIdValue)[0]
    print 'xtc is', xtc
    epix = xtc.get(0)
    parameterType = 'None'
    for member in epix :
        if member == 'asicPixelConfigArray':
            print 'Found the', 'asicPixelConfigArray', 'fpga parameter'
        else :
            print member, ' : ', epix[member]    
    print 'Composing the sequence of configurations ...'
    for cycle in range(steps) :
    	print 'Cycle ', cycle, 'pixels are ', (epix['asicPixelConfigArray'][0][0][0] & 3) | (cycle * 4)
        for asic in range(4) :
	    for row in range(epix['NumberOfRowsPerAsic']) :
            	for pixel in range(epix['NumberOfPixelsPerAsicRow']) :
		    epix['asicPixelConfigArray'][asic][row][pixel] = (epix['asicPixelConfigArray'][asic][row][pixel] & 3) | (cycle * 4)
        xtc.set(epix,cycle)
    cdb.substitute(newkey,xtc)
    cdb.unlock()
    print '    done'
#    exit()
#
#  Could scan EVR simultaneously
#
#    evr   = Evr  .ConfigV4().read(cdb.xtcpath(key.value,Evr  .DetInfo,Evr  .TypeId))
#    newxtc = cdb.remove_xtc(newkey,Evr.DetInfo,Evr.TypeId)

#
#  Send the structure the first time to put the control variables
#    in the file header
#
    daq.configure(key=newkey,
                      events=options.events,
                      controls=[])
    print "Configured."

#
#  Wait for the user to declare 'ready'
#    Setting up monitoring displays for example
#  
    ready = raw_input('--Hit Enter when Ready-->')

    for cycle in range(steps):
        print "Cycle", cycle
        daq.begin(events=options.events,controls=[])
        daq.end() 
        
#
#  Wait for the user to declare 'done'
#    Saving monitoring displays for example
#
    ready = raw_input('-- Finished, hit Enter to exit -->')
    print 'Restoring key', hex(key)
    daq.configure(key=key, events=1)
