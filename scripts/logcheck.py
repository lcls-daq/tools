#!/reg/g/pcds/package/python-2.5.2/bin/python
#

import subprocess
import datetime
import glob
from optparse import OptionParser
import re
import os

def control_log(path, summ):
    for fname in glob.iglob(path+'*control_gui.log'):
        fruns = []
        f = file(fname,"r")
        lines = f.readlines();
        run = {'duration':''}
        runnumber = '-'
        for iline in range(len(lines)):
            line = lines[iline]
            if (line.find("Configured")>=0 or line.find("Unmapped")>=0):
                if run['duration']!='':
                    fruns.append(run)
                    run = {'duration':''}
                    runnumber = '-'
            if (line.find("Completed allocating")>=0):
                runnumber = line.split()[-1]
            index = line.find("Duration")
            if (index>=0):
                ended    = line.partition(':Duration:')[0].rstrip()                
                duration = line.partition(' ')[-1].rstrip()
                events   = lines[iline+1].rpartition(':')[-1].rstrip()
                damaged  = lines[iline+2].rpartition(':')[-1].rstrip()
                bytes    = lines[iline+3].rpartition(':')[-1].rstrip().lstrip()
                bytes    = humansize(int(bytes), True)
                if int(events)==0:
                    evtsiz = ''
                else:
                    evtsiz = humansize(float(int(lines[iline+3].rpartition(':')[-1].rstrip())/int(events)),True)
#                    evtsiz   = ('%d'%(int(lines[iline+3].rpartition(':')[-1].rstrip())/int(events)))[:-3]
                srcs = []
                iline = iline+4
                line = lines[iline]
                while( (len(line)>17 and line[8]=='.' and line[17]==':') or
                       (len(line)>29 and line[2]=='_' and line[20]=='.' and line[29]==':') or
                       (len(line)>29 and line[20]=='.' and line[29]==':') or
                       (len(line)>41 and line[2]=='_' and line[32]=='.' and line[41]==':')):
                    s = line.rsplit(':')
                    srcs.append({'source':s[-2].rstrip(),'n':s[-1].rstrip()})
                    iline = iline+1
                    if (iline>=len(lines)):
                        break
                    line = lines[iline]
                run = {'runnumber':runnumber, 'ended':ended, 'duration':duration, 'evts':events, 'dmg':damaged, 'bytes':bytes, 'evtsz':evtsiz, 'sources':srcs}

        if run['duration']!='':
            fruns.append(run)

        sources = []
        for r in fruns:
            for s in r['sources']:
                if not s['source'] in sources:
                    sources.append(s['source'])

        if len(sources)==0:
            continue

        if summ:
            print_summary(fname, fruns, sources)
        else:
            print_full(fname, fruns, sources)
            

def print_full(fname,fruns,sources):
    print '\n-----'+fname,
    
    fmtttl = '\n%28.28s'
    fmtstr = '%12.12s'
    step = 5
        
    for irun in range(0,len(fruns),step):
        print " "
        runs = fruns[irun:irun+step]
        
        print fmtttl%'Run Number',
        for r in runs:
            print fmtstr%r['runnumber'],
        
        print fmtttl%'Duration',
        for r in runs:
            print fmtstr%r['duration'],
        
        print fmtttl%'Events',
        for r in runs:
            print fmtstr%r['evts'],

        print fmtttl%'Damaged',
        for r in runs:
            print fmtstr%r['dmg'],
        
        print fmtttl%'Bytes',
        for r in runs:
            print fmtstr%r['bytes'],

        print fmtttl%'EvtSz',
        for r in runs:
            print fmtstr%r['evtsz'],

        for src in sources:
            print fmtttl%src,
            for r in runs:
                lfound=False
                for s in r['sources']:
                    if s['source']==src:
                        lfound=True
                        print fmtstr%s['n'],
                if not lfound:
                    print fmtstr%'-',

def print_summary(fname, fruns,sources):
    print '\n-----'+fname,

    print "\n"
    fmt = '%11.11s %14.14s %15.15s %15.15s %15.15s %15.15s (%6s)  '
    print fmt%('Run Number', 'Duration', 'Ended', 'Bytes', 'Events', 'Damaged', '%')
    max1=0
    str1=''
    for irun in range(0, len(fruns)):
        r = fruns[irun]
        if int(r['evts']) == 0: pct = 0.0
        else: pct = "%3.2f" % (100.0*int(r['dmg'])/int(r['evts']))
        str = fmt%(r['runnumber'], r['duration'], r['ended'],r['bytes'], r['evts'], r['dmg'], pct)
        for s in r['sources']:
            if (s['source'].find('EBeam Low Curr')) == -1:
                if int(s['n']) > max1:
                    str1 = "%s (%s)," % (s['source'].split('.')[0], s['n'])
                    max1 = int(s['n'])
        str += str1
        print str
        max1=0
        str1=' '
    


def fixup_check(path):
    flist = glob.glob(path+'*.log')
    if len(flist)==0:
        return
    args = ["grep","fixup"]+flist
    pfn = subprocess.Popen(args=args,stdout=subprocess.PIPE)
    odate = pfn.communicate()[0].split('\n')
    laststr = None
    lastcnt = 1
    fmtstr='%20.20s'
    lttl = False
    for l in odate:
        if (l[:6]=='/reg/g'):
            thedate = l[29:39]
            thetime = l[40:48]
            thehost = l[49:].partition(':')[0]
            thename = l[49:].split(':')[1].split('.')[0]
            thisstr = fmtstr%thetime+fmtstr%thehost+fmtstr%thename
            if (thisstr==laststr):
                lastcnt = lastcnt+1
            else:
                if (laststr!=None):
                    if not lttl:
                        lttl=True
                        print '\n'+fmtstr%'Time'+fmtstr%'Node'+fmtstr%'Name'+fmtstr%'Fixups'
                    print laststr+fmtstr%lastcnt
                laststr=thisstr
                lastcnt=1
    if (laststr!=None):
        if not lttl:
            lttl=True
            print '\n'+fmtstr%'Time'+fmtstr%'Node'+fmtstr%'File'+fmtstr%'Fixups'
        print laststr+fmtstr%lastcnt


def signal_check(path, signum, signame):
    flist = glob.glob(path+'*.log')
    if len(flist)==0:
        return
    args = ["grep","signal"]+flist
    pfn = subprocess.Popen(args=args,stdout=subprocess.PIPE)
    odate = pfn.communicate()[0].split('\n')
    laststr = None
    lastcnt = 1
    fmtstr='%20.20s'
    lttl = False
    for l in odate:
        if (l[:6]=='/reg/g' and l.find('signal %d'%signum)>=0):
            thedate = l[29:39]
            thetime = l[40:48]
            thehost = l[49:].partition(':')[0]
            thename = l[49:].split(':')[1].split('.')[0]
            thisstr = fmtstr%thetime+fmtstr%thehost+fmtstr%thename
            if (thisstr==laststr):
                lastcnt = lastcnt+1
            else:
                if (laststr!=None):
                    if not lttl:
                        lttl=True
                        print '\n'+fmtstr%'Time'+fmtstr%'Node'+fmtstr%'Name'+fmtstr%signame
                    print laststr+fmtstr%lastcnt
                laststr=thisstr
                lastcnt=1
    if (laststr!=None):
        if not lttl:
            lttl=True
            print '\n'+fmtstr%'Time'+fmtstr%'Node'+fmtstr%'Name'+fmtstr%signame
        print laststr+fmtstr%lastcnt


def hutch_loop(expt, date_path, summ):
    hutches = ['amo','sxr','xpp','xcs','cxi','mec','cxi_0','cxi_1','cxi_shared']
    for hutch in hutches:
        if expt=='all' or expt==hutch.lower():

            print '=== %s ==='%hutch.upper()
            path = '/reg/g/pcds/pds/'+hutch+'/logfiles/'+date_path
            control_log(path,summ)
            fixup_check(path)
            signal_check(path,6,'SIGABORT')
            signal_check(path,11,'SIGSEGV')
            transition_check(path)
    if options.expt=='local':
        print '=== LOCAL ==='
        path = os.getenv('HOME')+'/'+date_path
        print path
        control_log(path,summ)
        fixup_check(path)
        signal_check(path,6,'SIGABORT')
        signal_check(path,11,'SIGSEGV')
        transition_check(path)
                                                                
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + datetime.timedelta(n)


SUFFIXES = {1024: ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
            1000: ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']}

def humansize(size, a_kilobyte_is_1024_bytes=True):
    '''Convert a file size to human-readable form.

    Arguments:
       size -- size in bytes
       a_kilobyte_is_1024_bytes -- if True (default), use multiples of 1024
                                if False, use multiples of 1000

    Returns: string repressenting file size

    '''
    if size < 0:
        raise ValueError('number must be non-negative')

    multiple = 1024 if a_kilobyte_is_1024_bytes else 1000
    for suffix in SUFFIXES[multiple]:
        size /= multiple
        if size < multiple:
            return '%8.1f %s'%(size, suffix)

    raise ValueError('number too large')

def pid2task(path,pid):
    flist=glob.glob(path+'*.log')
    tasks = []
    task = {'pid':0}
    args = ["grep","PID"]+flist
    p    = subprocess.Popen(args=args,stdout=subprocess.PIPE)
    output = p.communicate()[0].split('\n')
    for line in output:
        if line.find('@@@ The PID of new child')>=0:
            line = line.split("@@@ The PID of new child")[1]
            thedate = line.split('logfiles/')[1].split('_')[0]
            thetime = line.split('_')[1]
            thenode = line.split('_')[2].split(':')[0]
            thename = line.split('_')[2].split(':')[1].split('.')[0]
            thepid = line.split('is: ')[1].strip()
            task={'date':thedate, 'time':thetime, 'node':thenode,'name':thename,'pid':thepid}
            tasks.append(task)              
            if pid == thepid:
                return task
    return 0



def transition_check(path):
    fmtstr="%15.15s"
    longfmtstr="%25.25s"
    print '\n'+fmtstr%'Time'+longfmtstr%'Transition Timeout'+longfmtstr%'Task'+fmtstr%'PID'+longfmtstr%'Node'
    for fname in glob.iglob(path+'*control_gui.log'):
        logtime=fname.split(path)[1].split('_')[1]
        fruns = []
        f = file(fname,"r")
        lines = f.readlines();
        
        for iline in range(len(lines)):
            line = lines[iline]
            if (line.find("Completed allocating")>=0):
                runnumber = line.split()[-1]
            index = line.find("Timeout waiting for transition")
            if (index>=0):
                trans_time = line.partition(': Timeout')[0].rstrip().split('_')[1][:-9]
                transition = line.split(' to complete.')[0].strip().split('transition ')[1]
                nodes = lines[iline+1].rpartition(':')[-1].rstrip()
                segment, pid = lines[iline+2].split(':')[1:]
                segment = segment.strip()
                pid = pid.strip()
                task = pid2task(path+'_'+logtime, pid)
        
                print fmtstr%trans_time+longfmtstr%transition+longfmtstr%task['name']+fmtstr%task['pid']+longfmtstr%task['node']


if __name__ == "__main__":

    import sys

    parser = OptionParser()
    parser.add_option("-e","--expt",dest="expt",default="all",
                      help="Check logs for EXPT hutch", metavar="EXPT")
    parser.add_option("-d","--day",dest="day",default="0",
                      help="Check logs DAY days ago", metavar="DAY")
    parser.add_option("-s","--summ",default=False,action="store_true",
                      help="Print summary of control_log information", metavar="SUMM")
    parser.add_option("-b", "--beg",dest="beg_date",default="0",
                      help="Check logs from given date \%Y/\%M/\%d to end date (now if no end date given)",
                      metavar="BEG")
    parser.add_option("-f", "--end",dest="end_date",default="0",
                      help="Check logs from given date \%Y/\%M/\%d to end (finish) date", metavar="END")
    (options, args) = parser.parse_args()
    
    
    thisdate = datetime.date.today() - datetime.timedelta(int(options.day))
    date_path = thisdate.strftime('%Y/%m/%d')

    if options.beg_date!="0":
        year,month,day=options.beg_date.replace('-','/').strip().split('/')
        beg_date = datetime.date(int(year), int(month), int(day))

        if options.end_date!="0":
            end_year, end_month, end_day = options.end_date.replace('-','/').strip().split('/')
            end_date = datetime.date(int(end_year),int(end_month),int(end_day))
        else:
            end_date = datetime.date.today()
    
        for single_date in daterange(beg_date,end_date):
            date_path = single_date.strftime("%Y/%m/%d")
            hutch_loop(options.expt.lower(), date_path, options.summ)
    else:
        hutch_loop(options.expt.lower(), date_path, options.summ)
        
