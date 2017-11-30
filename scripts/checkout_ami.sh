#!/bin/bash

# $Id$

function show_help()
{
    echo    "Usage: $0 -u URL -d DEST [-b BRANCH | -t TAG] [-h]"
}

# if no branch or tag is specified, checkout from master branch
flavor="master"

OPTIND=1
while getopts ":hu:d:b:t:" opt; do
    case "$opt" in
    h)
        # help
        show_help
        exit 0
        ;;
    \?)
        # unrecognized option
        show_help
        exit 1
        ;;
    u)  url=$OPTARG
        ;;
    d)  release_dir=$OPTARG
        ;;
    b)  flavor="$OPTARG"
        ;;
    t)  flavor="$OPTARG"
        ;;
    esac
done

shift $((OPTIND-1))

[ "$1" = "--" ] && shift

if test "$#" -ne 0; then 
    error=1
fi

if [ -z "$url" ]; then
    echo "$0: cannot access repository: URL not defined"
    error=1
fi

if [ -z "$release_dir" ]; then
    echo "$0: cannot create directory: DEST not defined"
    error=1
fi

if [ -a "$release_dir" ]; then
    echo "$0: cannot create directory \`$release_dir': File exists"
    error=1
fi

if [ -n "$error" ]; then
    show_help
    exit 1
fi

# exit immediately if a command exits with a non-zero status
set -e

/usr/bin/git clone --recursive $url/ami-release.git $release_dir
if [ -n "$flavor" ]; then
  cd $release_dir
  /usr/bin/git checkout "$flavor"
  /usr/bin/git submodule foreach -q --recursive "git checkout $flavor"
fi

exit 0
