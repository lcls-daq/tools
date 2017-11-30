#!/usr/bin/python
#

import os
import subprocess
import sys
from optparse import OptionParser

usage = "%prog [options] tag"
parser = OptionParser(usage=usage)

parser.add_option("-n", "--dry-run",
                  action="store_true", dest="dry_run", default=False,
                  help="do not modify repository")
parser.add_option("-f", "--force",
                  action="store_true", dest="force", default=False,
                  help="skip sanity checks (use with caution!)")

tag=None
DAQURL='https://pswww.slac.stanford.edu/svn/pdsrepo'

daq_subdirs = ['pds', 'pdsapp', 'timetool', 'tools']
ami_subdirs = ['ami', 'tools']


def push(pkg):
    return subprocess.call(['/usr/bin/git push origin '+tag], cwd = pkg, shell = True)

def make_tag(pkg):
    cmd = ['/usr/bin/git tag '+tag+' -m "Tag %s"'%tag]
    return subprocess.call(cmd, cwd = pkg, shell = True)

def verify_tag(pkg):
    rv = False
    p = subprocess.Popen(['/usr/bin/git tag -l '+tag], cwd = pkg, shell = True,
                         stdout = subprocess.PIPE, stderr = subprocess.PIPE, close_fds = True)
    if subprocess.Popen.communicate(p)[0]:
        rv = True
    return rv

def make_tagd(pkg):
    retval = 0
    if (os.path.isdir(pkg)):
        retval = make_tag(pkg)
    else:
        print 'Warning: directory \'%s\' not found, tagging skipped' % pkg
    return retval

def fetch(project_path):
    p = subprocess.Popen(['/usr/bin/git fetch origin'], cwd = project_path, shell = True, stdout = subprocess.PIPE, close_fds = True)
    return subprocess.Popen.communicate(p)[0]

def fetch_tags(project_path):
    p = subprocess.Popen(['/usr/bin/git fetch origin --tags'], cwd = project_path, shell = True, stdout = subprocess.PIPE, close_fds = True)
    return subprocess.Popen.communicate(p)[0]

def status(project_path):
    p = subprocess.Popen(['/usr/bin/git status --porcelain'], cwd = project_path, shell = True, stdout = subprocess.PIPE, close_fds = True)
    return subprocess.Popen.communicate(p)[0]

def get_current_branch(project_path):
    p = subprocess.Popen(['/usr/bin/git rev-parse --abbrev-ref HEAD'], cwd = project_path, shell = True, stdout = subprocess.PIPE, close_fds = True)
    return subprocess.Popen.communicate(p)[0]

def compare_rev(project_path):
    p = subprocess.Popen(['/usr/bin/git rev-parse master'], cwd = project_path, shell = True, stdout = subprocess.PIPE, close_fds = True)
    loc = subprocess.Popen.communicate(p)[0]
    p = subprocess.Popen(['/usr/bin/git rev-parse origin/master'], cwd = project_path, shell = True, stdout = subprocess.PIPE, close_fds = True)
    rem = subprocess.Popen.communicate(p)[0]
    return loc != rem


if __name__ == '__main__':

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    else:
        tag = args[0]

    if tag.find('ami') >= 0:
        dirlist = ami_subdirs + ['.']
    else:
        dirlist = daq_subdirs + ['.']

    if not options.force:
        fail = False
        # sanity check 0: tag begins with 'V' or 'ami-V'
        if tag.find('V') and tag.find('ami-V'):
            print 'sanity check failed: tag \'%s\' does not begin with \'V\' or \'ami-V\'' % tag 
            fail = True

        # sanity check 1: check that local branches synced with remote
        for dir in dirlist:
            fetch(dir)
            fetch_tags(dir)
            if compare_rev(dir):
                print 'sanity check failed: working directory \'%s\' out of sync with remote' % dir
                fail = True

        # sanity check 2: check that current directory and submodules are clean
        for dir in dirlist:
            if status(dir):
                print 'sanity check failed: working directory \'%s\' has uncommited changes' % dir
                fail = True

        # sanity check 3: tag does not already exist
        for dir in dirlist:
            if verify_tag(dir):
                print 'sanity check failed: tag \'%s\' already exists for directory \'%s\'' % (tag, dir)
                fail = True

        # sanity check 4: current directory is on branch master
        cwdprop = get_current_branch(".")
        if (not cwdprop) or (cwdprop.find('master') == -1):
            print 'sanity check failed: working directory is not on the master branch' 
            fail = True

        # sanity check 5: current directory contains expected subdirectories
        for dir in dirlist:
            if dir != 'release' and dir != 'ami-release' and dir != '.' and not os.path.isdir(dir):
                print 'sanity check failed: working directory does not include \'%s\' subdirectory' % dir
                fail = True
            cwdprop = get_current_branch(dir)
            if (not cwdprop) or (cwdprop.find('master') == -1):
                print 'sanity check failed: working directory \'%s\' is not on the master branch' % dir
                fail = True

        if fail: 
            print 'tag \'%s\' not applied (sanity check failure)' % tag
            sys.exit(1)

    if options.dry_run:
        print 'tag \'%s\' not applied (dry run)' % tag
        sys.exit(0)

    retval = 0
    if tag.find('ami')<0:
        if make_tag('.'):
            retval = 1
            print 'Error: tagging release failed'
        else:
            for dir in daq_subdirs:
                if make_tagd(dir):
                    retval = 1
                    print 'Error: tagging %s failed' % dir
            # update remote
            if push('.'):
                retval = 1
                print 'Error: pushing release failed'
            else:
                for dir in daq_subdirs:
                    if push(dir):
                        retval = 1
                        print 'Error: pushing %s failed' % dir
            retval = 0  # success
    else:
        if make_tag('.'):
            retval = 1
            print 'Error: tagging ami-release failed'
        else:
            for dir in ami_subdirs:
                make_tagd(dir)
            # update remote
            if push('.'):
                retval = 1
                print 'Error: pushing ami-release failed'
            else:
                for dir in ami_subdirs:
                    if push(dir):
                        retval = 1
                        print 'Error: pushing %s failed' % dir
            retval = 0  # success
    sys.exit(retval)
