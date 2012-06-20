#!/bin/bash
source /etc/trac/env.sh

BASE="${ROOT}/trac"

if [ ! -d "${BASE}" ] || [ ! -d "$BASE/results" ] ; then
   exit
fi

PYFILE="${BASE}/dist/current/scripts/storageusage.py"
START="$(date +'%d.%m.%Y %H:%M:%S')"

PIDFILE="/tmp/storageusage.pid"
LOGFILE="/tmp/storageusage.log"

if [ -r "$PIDFILE" ] ; then
  SUPID=$(cat $PIDFILE)
  if [ -n "$SUPID" ]; then
    if [ -n "$(ps -lp $SUPID |tail -1| grep $SUPID)" ] ; then
      echo "  Earlier session active ($START)" >> $LOGFILE
      exit
    fi
  fi
fi
echo "$$" > $PIDFILE

echo "Operation started at $START" >> $LOGFILE

if [ -x /usr/bin/ionice ] &&
    /usr/bin/ionice -c3 true 2>/dev/null; then
    NICE="/usr/bin/ionice -c3"
else
    NICE="nice -n 8"
fi

if [ -r "$BASE/results/storageusage.tmp" ] ; then
   :> $BASE/results/storageusage.tmp
fi

for project in $BASE/projects/*
do
    NAME="$(echo "$project" | tr '/' '\n' | tail -1)"
    psize="$($NICE find $BASE/projects/$NAME -size +0 -printf "%s\\n"|awk '{sum+=$0}END{printf "%.0f\n",sum}')"

    if [ -d "$BASE/repositories/$NAME" ] ; then
      rsize="$($NICE find $BASE/repositories/$NAME -size +0 -printf "%s\\n"|awk '{sum+=$0}END{printf "%.0f\n",sum}')"
    else
      rsize=0
    fi
    if [ -d "$BASE/webdav/$NAME" ] ; then
      dsize="$($NICE find $BASE/webdav/$NAME -size +0 -printf "%s\\n"|awk '{sum+=$0}END{printf "%.0f\n",sum}')"
    else
      dsize=0
    fi
    echo "$NAME,$psize,$rsize,$dsize" >> $BASE/results/storageusage.tmp
done

if [ -r "$BASE/results/storageusage.tmp" ] ; then
  mv $BASE/results/storageusage.tmp  $BASE/results/storageusage.csv
fi

rm -f $PIDFILE

if [ -r "${PYFILE}" ] ; then
  python ${PYFILE}
else
  echo "  Storage notifications cannot be used (file not found)"
fi

echo "Operation ended at $(date +'%d.%m.%Y %H:%M:%S')" >> $LOGFILE
