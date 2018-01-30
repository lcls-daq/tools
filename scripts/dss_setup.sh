#!/bin/bash
if [ $# -ne 1 ]; then
  echo "usage $0 <hutch>"
  exit 2
fi

HUTCH="$1"

if [ -d /u2 ]; then
  cd -P -- /u2
  if [ ! -d "pcds/pds/$HUTCH" ]; then
    mkdir -p "pcds/pds/$HUTCH"
  fi
  cd -P -- "pcds/pds"
  chown "${HUTCH}opr:xs" "$HUTCH"
  chmod g+w "$HUTCH"
  setfacl -R -m user::rwx "$HUTCH"
  setfacl -R -m user:psdatmgr:rwx "$HUTCH"
  setfacl -R -m group::rwx "$HUTCH"
  setfacl -R -m mask::rwx "$HUTCH"
  setfacl -R -m other::r-x "$HUTCH"
  setfacl -R -m default:user::rwx "$HUTCH"
  setfacl -R -m default:user:psdatmgr:rwx "$HUTCH"
  setfacl -R -m default:group::rwx "$HUTCH"
  setfacl -R -m default:mask::rwx "$HUTCH"
  setfacl -R -m default:other::r-x "$HUTCH"
else
  echo "/u2 does not exist! - Disks likely not mounted"
  exit 1
fi
