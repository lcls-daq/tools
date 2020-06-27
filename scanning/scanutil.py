import pydaq
import pycdb
import math
import serial
import pprint
import numpy as np

from optparse import OptionParser

nindent = 0
match = False   
gvalue = 0

def get_member(d,name,m,v):
    global match
    global gvalue
#    print 'name:'+name
#    print 'm   :'+m
    if isinstance(v,list):
        if name.split('[')[0]==m.split('[')[0]:
            index = name.split('[')[1].split(']')[0]
            n = v[int(index)]
            #  Don't try 2d arrays yet
            if isinstance(n,list):
                pass;
            if isinstance(n,dict):
                nname = name.partition('.')[2]
                for member,value in n.items():
                    get_member(n,nname,member,value)
            else:
                gvalue = d[m]
                match = True
    elif isinstance(v,dict):
        fields = name.partition('.')
        if fields[0]==m:
            for member,value in v.items():
                get_member(v,fields[2],member,value)
    elif name==m:
        gvalue = d[m]
        match = True
#    print match 

def get_dict(d,name):
    global match
    global gvalue
    match = False
    for member,value in d.items():
        get_member(d,name,member,value)
        if match:
            return gvalue
    print 'No match found'
    return -1

def set_member(d,name,t,m,v):
    global match
#    print 'name:'+name
#    print 'm   :'+m
    if isinstance(v,list):
        if name.split('[')[0]==m.split('[')[0]:
            index = name.split('[')[1].split(']')[0]
            for i in range(len(v)):
                if index=='*' or i==int(index):
                    n = v[i]
                    #  Don't try 2d arrays yet
                    if isinstance(n,list):
                        pass;
                    if isinstance(n,dict):
                        nname = name.partition('.')[2]
                        for member,value in n.items():
                            set_member(n,nname,t,member,value)
                            
                    else:
                        d[m] = t
                        match = True
    elif isinstance(v,dict):
        fields = name.partition('.')
        if fields[0]==m:
            for member,value in v.items():
                set_member(v,fields[2],t,member,value)
    elif name==m:
        d[m] = t
        match = True
#    print match 

def set_dict(d,name,target):
    global match
    match = False
    for member,value in d.items():
        set_member(d,name,target,member,value)        
    return match
            

def dump_member(m,v):
    global nindent
    if nindent==0:
        print m,
    else:
        for i in range(nindent):
            print '\t',
        print '.'+m,
    if not isinstance(v,list) and not isinstance(v,dict):
        print
    else:
        if isinstance(v,list):
            print '[%u]'%len(v),
            n = v[0]
            while isinstance(n,list):
                print '[%u]'%len(n),
                n = n[0]
            print
            if not isinstance(n,dict):
                return
        elif isinstance(v,dict):
            print
            n = v
        nindent += 1
        for member,value in n.items():
            dump_member(member,value)
        nindent-=1

def dump_dict(d):
    for member,value in d.items():
        dump_member(member,value)

def scan_exponential(device, configtype):

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
    parser.add_option("-i","--deviceID",dest="deviceID",type="int",default=0,
                      help="device ID to scan, default 0",metavar="DEV_ID")
    parser.add_option("-t","--typeIdVersion",dest="typeIdVersion",type="int",default=1,
                      help="type ID Version in use, default 1",metavar="typeIdVersion")
    parser.add_option("-P","--parameter",dest="parameter",type="string",
                      help="epix parameter to scan", metavar="PARAMETER")
    parser.add_option("-A","--dbalias",dest="dbalias",type="string",
                      help="data base key in use",metavar="DBALIAS")
    parser.add_option("-s","--start",dest="start",type="float", default=200,
                      help="parameter start", metavar="START")
    parser.add_option("-f","--finish",dest="finish",type="int",nargs=1,default=2000,
                      help="parameter finish", metavar="FINISH")
    parser.add_option("-m","--multiplier",dest="multiplier",type="float",nargs=1,default=-1.0,
                      help="parameter multiplier in case you want to enter it directly, ignoring FINISH", metavar="MULTIPLIER")
    parser.add_option("-n","--steps",dest="steps",type="int",default=20,
                      help="run N parameter steps", metavar="N")
    parser.add_option("-e","--events",dest="events",type="int",default=105,
                      help="record N events/cycle", metavar="EVENTS")
    parser.add_option("-L","--linear",dest="linear",type="string",default="no",
              help="Set to yes for linear scanning instead of exponential", metavar="LINEAR")
    parser.add_option("-l","--limit",dest="limit",type="int",default=99,
                      help="limit number of configs to less than number of steps", metavar="LIMIT")
    parser.add_option("-S","--shutter",dest="shutter",default="None",
                      help="path to shutter serial port", metavar="SHUTTER")
    parser.add_option("-u","--use_l3t",dest="use_l3t",action="store_true",default=False,
                      help="Use L3Trigger to filter events",metavar="L3T")

    (options, args) = parser.parse_args()
    
    options.device = device
    options.typeId = configtype
    
    print 'host', options.host
    print 'platform', options.platform
    print 'dbalias',options.dbalias
    print 'parameter', options.parameter
    print 'start', options.start, options.start
    print 'steps', options.steps
    print 'finish', options.finish
#    print 'multiplier', options.multiplier
    print 'events', options.events
    print 'detector', options.detector
    print 'detectorID', options.detectorID
    print 'device', options.device
    print 'deviceID', options.deviceID
#    print 'linear', options.linear
    print 'shutter', options.shutter
    print 'use_l3t', options.use_l3t

    if options.steps < options.limit : options.limit = options.steps
    else : print 'Warning, range will be covered in', options.limit, \
         'but will still do', options.steps, 'steps with wrapping'

    adder = 0.0
    if options.linear == "no" :
      if (options.start == 0) :
        options.start = 0.49
      if (options.multiplier < 0) :
        options.multiplier = math.exp( (math.log( float(options.finish)/options.start )) / options.limit  )
      print 'multiplier in use is', options.multiplier, 'and will scan from', options.start, 'to', options.finish
    else :
        adder = (float(options.finish) - options.start) / float(options.limit)
        print 'will do linear scanning from', options.start, 'to', options.finish, "in ", options.limit, "steps and with adder of ", adder

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

    if set_dict(epix,options.parameter,float(options.start))==False:
        dump_dict(epix)
        sys.exit(1)

    else :
        print 'Composing the sequence of configurations ...'
        value = float(options.start)
        cycleLength = 1
        shutterActive = options.shutter != 'None'
        if shutterActive :
            cycleLength = 2
        denom = float(options.limit+1)
#        mask = epix['AsicMask']
        values = []
        for cycle in range(options.limit+1) :
            print cycle
            index = float(cycle%(options.limit+1)) + 1.0
            set_dict(epix,options.parameter,value)
            xtc.set(epix,cycle)
            values.append(value);
            if options.linear == "no" :
#                print cycle, int(round(value))
                value = value * options.multiplier
            else :
#                print cycle, int(round(value)) 
                value = value + adder
        cdb.substitute(newkey,xtc)
        cdb.unlock()
        for cycle in range(len(values)) :
            print cycle, "value of", options.parameter, "is",  values[cycle]
        print '    done'
#
#  Could scan EVR simultaneously
#
#    evr   = Evr  .ConfigV4().read(cdb.xtcpath(key.value,Evr  .DetInfo,Evr  .TypeId))
#    newxtc = cdb.remove_xtc(newkey,Evr.DetInfo,Evr.TypeId)

#
#  Send the structure the first time to put the control variables
#    in the file header
#

        if options.use_l3t:
            print "Acquiring %s events passing L3Trigger"%(options.events)
            daq.configure(key=newkey,
                          l3t_events=options.events,
                          controls=[(options.parameter[0:29],int(round(options.start)))])
        else:
            daq.configure(key=newkey,
                          events=options.events,
                          controls=[(options.parameter[0:29],int(round(options.start)))])

        print "Configured."

# set up shutter
        if shutterActive :
            ser = serial.Serial(options.shutter)
            ser.write(chr(129)) ## close shutter

#
#  Wait for the user to declare 'ready'
#    Setting up monitoring displays for example
#  
        ready = raw_input('--Hit Enter when Ready-->')
        for cycle in range(options.steps+1):
          if cycle%(options.limit+1) == 0 : 
            index = 0.0
            subcycle = 0;
          if shutterActive :
            ser.write(chr(129)) ## close shutter
            print "Cycle", cycle, " closed -", options.parameter, "=", values[subcycle]
          else :
            print "Cycle", cycle, "-", options.parameter, "=", values[subcycle]
          if options.use_l3t:
              daq.begin(l3t_events=options.events,controls=[(options.parameter[0:29],values[subcycle])])
          else:
              daq.begin(controls=[(options.parameter[0:29],values[subcycle])])
          # wait for enabled , then enable the EVR sequence
          # wait for disabled, then disable the EVR sequence
          daq.end() 
          if shutterActive :
            print "        opened -", options.parameter, "=", values[subcycle]
            ser.write(chr(128)) ## open shutter
            if options.use_l3t:
                daq.begin(l3t_events=options.events,controls=[(options.parameter[0:29],values[subcycle])])
            else:
                daq.begin(controls=[(options.parameter[0:29],values[subcycle])])
            daq.end()
            ser.write(chr(129)) ## close shutter
          subcycle += 1;
        
#
#  Wait for the user to declare 'done'
#    Saving monitoring displays for example
#
    ready = raw_input('-- Finished, hit Enter to exit -->')
    print 'Restoring key', hex(key)
    daq.configure(key=key, events=1)

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

def scan_offset(device, configtype):
    import sys

    parser = OptionParser()
    parser.add_option("-a","--address",dest="host",default='localhost',
                      help="connect to DAQ at HOST", metavar="HOST")
    parser.add_option("-p","--platform",dest="platform",type="int",default=0,
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
    parser.add_option("-s","--space",dest="space",type="int", default=7,
                      help="space is the spacing in the array", metavar="SPACE")
    parser.add_option("-e","--events",dest="events",type="int",default=4608,
                      help="record N events/cycle", metavar="EVENTS")
    parser.add_option("-v","--value0",dest="Value0",type="int",default=0,
                      help="Value0 for most of the pixel array, default=0 ", metavar="VALUE0")
    parser.add_option("-V","--value1",dest="Value1",type="int",default=1,
                      help="Value1 for pixels under test in the pixel array, default=1", metavar="VALUE1")
    parser.add_option("-d","--darkEvents",dest="darkEvents",type="int",default=1200,
                      help="Number of events in each Dark, default=1200 ", metavar="DARKEVENTS")
    parser.add_option("-u","--user",dest="userFlag",type="int",default=1,
                      help="Iff zero then no user, default=1", metavar="USERFLAG")
    parser.add_option("-o","--cycleStart",dest="cycleStart",type="int",default=0,
                      help="Starting at cycle number, default=0", metavar="CYCLESTART")
    parser.add_option("-O","--cycleStop",dest="cycleStop",type="int",default=105,
                      help="Stopping at cycle number, default=105", metavar="CYCLESTOP")

    (options, args) = parser.parse_args()
    
    options.device = device
    options.typeId = configtype
    
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
    print 'cycleStart', options.cycleStart
    print 'cycleStop', options.cycleStop

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
        'Auto Medium to Low'
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
    gcycle = 0   # cycle number if nothing skipped
    cycle = 0    # cycle number excluding skipped
    for dark in range(numberOfDarks) :
        if gcycle >= options.cycleStart and gcycle < options.cycleStop:
            if 'elemCfg' in epix:
                for e in epix['elemCfg']:
                    mask = e['asicMask']
                    for rows in range(352) :
                        for cols in range(384) :
                            e['asicPixelConfigArray'][rows][cols] = darkValues[dark]
                    for asicNum in range(4) :
                        if mask & (1 << asicNum) :
                            e['asics'][asicNum]['trbit']=trBitValues[dark]
            else:
                mask = epix['AsicMask']
                for rows in range(352) :
                    for cols in range(384) :
                        epix['asicPixelConfigArray'][rows][cols] = darkValues[dark]
                for asicNum in range(4) :
                    if mask & (1 << asicNum) :
                        epix['asics'][asicNum]['trbit']=trBitValues[dark]
            xtc.set(epix, cycle)   
            cycle += 1
        gcycle += 1
        
    for trbit in [0, 1] :
        for position in range(options.space**2) :
            if gcycle >= options.cycleStart and gcycle < options.cycleStop:
                maskedpixels = pixel_mask(options.Value0, options.Value1, options.space, position)
                if 'elemCfg' in epix:
                    for e in epix['elemCfg']:
                        mask = e['asicMask']
                        for rows in range(352) :
                            for cols in range(384) :
                                e['asicPixelConfigArray'][rows][cols] = maskedpixels[rows][cols]
                        for asicNum in range(4) :
                            if mask & (1 << asicNum) :
                                e['asics'][asicNum]['atest']=1
                                e['asics'][asicNum]['test']=1
                                e['asics'][asicNum]['trbit']=trbit
                                e['asics'][asicNum]['Pulser']=0
                else:
                    mask = epix['AsicMask']
                    for rows in range(352) :
                        for cols in range(384) :
                            epix['asicPixelConfigArray'][rows][cols] = maskedpixels[rows][cols]
                    for asicNum in range(4) :
                        if mask & (1 << asicNum) :
                            epix['asics'][asicNum]['atest']=1
                            epix['asics'][asicNum]['test']=1
                            epix['asics'][asicNum]['trbit']=trbit
                            epix['asics'][asicNum]['Pulser']=0
                xtc.set(epix, cycle)
                cycle += 1
            gcycle += 1
#            print 'xtc.set(, epix', position + (trbit*(options.space**2)), ')'
    cdb.substitute(newkey,xtc)
    cdb.unlock()
    print '    done'

#  Send the structure the first time to put the control variables
#    in the file header
#

    cycle_label = [
        ('Epix10ka2M offset scan',''),
    ]
    daq.configure(key=newkey, events=options.events, labels=cycle_label)

    print "Configured."

#
#  Wait for the user to declare 'ready'
#    Setting up monitoring displays for example
#  
    if options.userFlag > 0 :
        ready = raw_input('--Hit Enter when Ready-->')

    gcycle = 0
    for dark in range(numberOfDarks) :
        if gcycle >= options.cycleStart and gcycle < options.cycleStop:
            print 'dark', darkMessages[dark]
            cycle_label = [
                ('Epix10ka2M offset scan', 'dark %s' %  darkMessages[dark]),
            ]
            daq.begin(events=options.darkEvents, labels=cycle_label)
            daq.end() 
        gcycle += 1
       
    for trbit in [0, 1] :
        for position in range(((options.space**2))):
            if gcycle >= options.cycleStart and gcycle < options.cycleStop:
                print 'position', position, 'trbit', trbit
                cycle_label = [
                    ('Epix10ka2M offset scan', 'position %d trbit %d' % (position, trbit)),
                ]
                daq.begin(events=options.events, labels=cycle_label)
                daq.end() 
            gcycle += 1
        
#
#  Wait for the user to declare 'done'
#    Saving monitoring displays for example
#
    if options.userFlag > 0 :    
        ready = raw_input('-- Finished, hit Enter to exit -->')
    print 'Restoring key', hex(key)
    daq.configure(key=key, events=1)

def scan_parameter(device, configtype, parameter, values, enumkey=None):
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
    parser.add_option("-i","--deviceID",dest="deviceID",type="int",default=0,
                      help="device ID to scan, default 0",metavar="DEV_ID")
    parser.add_option("-t","--typeIdVersion",dest="typeIdVersion",type="int",default=1,
                      help="type ID Version in use, default 1",metavar="typeIdVersion")
    parser.add_option("-A","--dbalias",dest="dbalias",type="string",
                      help="data base key in use",metavar="DBALIAS")
    parser.add_option("-e","--events",dest="events",type="int",default=1000,
                      help="record N events/cycle", metavar="EVENTS")
    parser.add_option("-u","--user",dest="userFlag",type="int",default=1,
                      help="Iff zero then no user, default=1", metavar="DARKEVENTS")

    (options, args) = parser.parse_args()

    options.device = device
    options.typeId = configtype

    print 'host', options.host
    print 'platform', options.platform
    print 'dbalias',options.dbalias
    print 'detector', options.detector
    print 'detectorID', options.detectorID
    print 'device', options.device
    print 'deviceID', options.deviceID
    print 'events', options.events
    print 'userFlag', options.userFlag

    print 'device', device
    print 'configtype', configtype
    print 'parameter', parameter
    print 'values', values

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
    config = xtc.get(0)
    if enumkey is not None:
        enums = xtc.get_enums()[enumkey]
    else:
        enums = None
    print 'Composing the sequence of configurations ...'
    cycle = 0    # cycle number excluding skipped
    for value in values:
        if parameter in config:
            if enums is not None:
                config[parameter] = enums[value]
            else:
                config[parameter] = value
        print config, cycle
        xtc.set(config, cycle)
        cycle += 1

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

    for value in values:
        print 'parameter', parameter, 'value', value
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
