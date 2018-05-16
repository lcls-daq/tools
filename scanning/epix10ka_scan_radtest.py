#!/reg/g/pcds/package/python-2.5.2/bin/python
#

import pydaq
import pycdb
import math
import serial
import pprint
import numpy as np

def pixel_mask(value0,value1,spacing,position):
    ny,nx=352,384;
    if position>=spacing**2:
        print 'position out of range';
        position=0;
#    print 'pixel_mask(', value0, value1, spacing, position, ')'
    out=np.zeros((ny,nx),dtype=np.int)+value0;
    position_x=position%spacing; position_y=position//spacing;
    out[position_y::spacing,position_x::spacing]=value1;
    return out;

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
#    parser.add_option("-d","--device",dest="device",type="string",default='Epix10ka',
#                      help="device to scan, default Epix10ka",metavar="DEV")
    parser.add_option("-i","--deviceID",dest="deviceID",type="int",default=0,
                      help="device ID to scan, default 0",metavar="DEV_ID")
    parser.add_option("-t","--typeIdVersion",dest="typeIdVersion",type="int",default=1,
                      help="type ID Version in use, default 1",metavar="typeIdVersion")
    parser.add_option("-A","--dbalias",dest="dbalias",type="string",
                      help="data base key in use",metavar="DBALIAS")
    parser.add_option("-s","--space",dest="space",type="int", default=4,
                      help="space is the spacing in the array", metavar="SPACE")
    parser.add_option("-e","--events",dest="events",type="int",default=3072,
                      help="record N events/cycle", metavar="EVENTS")
    parser.add_option("-v","--value0",dest="Value0",type="int",default=0,
                      help="Value0 for most of the pixel array ", metavar="VALUE0")
    parser.add_option("-V","--value1",dest="Value1",type="int",default=1,
                      help="Value1 for pixels under test in the pixel array ", metavar="VALUE1")
    parser.add_option("-d","--darkEvents",dest="darkEvents",type="int",default=1200,
                      help="Number of events in each Dark, default=1200 ", metavar="DARKEVENTS")
    parser.add_option("-u","--user",dest="userFlag",type="int",default=1,
                      help="Iff zero then no user, default=1", metavar="DARKEVENTS")

    (options, args) = parser.parse_args()
    
    options.device = 'Epix10ka'
    options.typeId = 'Epix10kaConfig'
    
    print 'host', options.host
    print 'platform', options.platform
    print 'dbalias',options.dbalias
    print 'detector', options.detector
    print 'detectorID', options.detectorID
    print 'device', options.device
    print 'deviceID', options.deviceID
    if options.space > 7 :
        print 'Space is too large, truncated to 7'
        options.space = 7
    print 'space', options.space
    print 'Values', options.Value0, ',', options.Value1
    print 'darkEvents', options.darkEvents
    print 'events', options.events
    print 'userFlag', options.userFlag
    
#Fixed High Gain , pixel matrix to 0xc trbit 1
#Fixed Medium Gain pixel matrix to 0xc trbit 0
#Fixed Low Gain pixel matrix to to 0x8 trbit don't care
#Auto High to Low pixel matrix to 0x0 trbit 1
#Auto Medium to low pixel matrix to 0x0 trbit 0
    numberOfDarks = 5
    darkValues = [0xc, 0xc, 0x8, 0, 0]
    trBitValues = [1, 0, 0, 1, 0]
    darkMessages = [
        'Fixed High Gain',
        'Fixed Medium Gain',
        'Fixed Low Gain',
        'Auto High to Low',
        'Auto Medium to low'
        ]
        

# Connect to the daq system
    daq = pydaq.Control(options.host,options.platform)
    daq.connect()
    print 'Partition is', daq.partition()
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
    xtc = cdb.get(key=key,src=detectorValue,typeid=typeIdValue)[0]
    print 'xtc is', xtc
    epix = xtc.get(0)
    print 'Composing the sequence of configurations ...'
    mask = epix['AsicMask']
    for dark in range(numberOfDarks) :
        for rows in range(352) :
            for cols in range(384) :
                epix['asicPixelConfigArray'][rows][cols] = darkValues[dark]
        for asicNum in range(4) :
            if mask & (1 << asicNum) :
                epix['asics'][asicNum]['trbit']=trBitValues[dark]
        xtc.set(epix, dark)   
    for trbit in [0, 1] :
        for position in range(options.space**2) :
            maskedpixels = pixel_mask(options.Value0, options.Value1, options.space, position)
            for rows in range(352) :
                for cols in range(384) :
                    epix['asicPixelConfigArray'][rows][cols] = maskedpixels[rows][cols]
            for asicNum in range(4) :
                if mask & (1 << asicNum) :
                    epix['asics'][asicNum]['atest']=1
                    epix['asics'][asicNum]['test']=1
                    epix['asics'][asicNum]['trbit']=trbit
                    epix['asics'][asicNum]['Pulser']=0
            xtc.set(epix, numberOfDarks + position + (trbit*(options.space**2)))
#            print 'xtc.set(, epix', position + (trbit*(options.space**2)), ')'
    cdb.substitute(newkey,xtc)
    cdb.unlock()
    print '    done'

#  Send the structure the first time to put the control variables
#    in the file header
#

    daq.configure(key=newkey, events=options.events)

    print "Configured."

#
#  Wait for the user to declare 'ready'
#    Setting up monitoring displays for example
#  
    if options.userFlag > 0 :
        ready = raw_input('--Hit Enter when Ready-->')

    for dark in range(numberOfDarks) :
        print 'dark', darkMessages[dark]
        daq.begin(events=options.darkEvents)
        daq.end() 
       
    for trbit in [0, 1] :
        for position in range(((options.space**2))):
            print 'position', position, 'trbit', trbit
            daq.begin(events=options.events)
            daq.end() 
        
#
#  Wait for the user to declare 'done'
#    Saving monitoring displays for example
#
    if options.userFlag > 0 :    
        ready = raw_input('-- Finished, hit Enter to exit -->')
    print 'Restoring key', hex(key)
    daq.configure(key=key, events=1)
