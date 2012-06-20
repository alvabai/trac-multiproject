#!/bin/bash

function helpme()
{
  echo "This is a custom script for updating the existing multiproject powered Trac setup."
  echo ""
  echo "Parameters:"
  echo "  -a or --activate        : Updates automatically 'current' link. Default false"
  echo "  -b or --batchmodify     : Install batch modify plugin. Default false"
  echo "  -c or --childtickets    : Install also childtickets plugin in to trac. Default false"
  echo "  -d or --datelink        : Uses only date instead date and time in directory link. Default false"
  echo "  -t or --theme           : Install default theme or not. Default false."
  echo "  -h or --help            : Show this help message"
  echo ""
  echo "NOTE:"
  echo "  The parameters used and set with arguments can also be set as system environment variables"
}

# Parameters
SRC=""
BATCHMODIFY=0
CHILDTICKETS=0
DATELINKS=0
ACTIVATE=0
THEME=0
SUDO="sudo"
WEBSRV_USER=www-data
WEBSRV_GROUP=www-data
ENV_PTH="/etc/trac/env.sh"
EXTENSIONS="TracMultiProject TracDiscussion TracDownloads"

for par in $* ; do
    case $par in
      "-b" |  "--bm" |"--batchmodify") BATCHMODIFY=1  ;;
     "-c" |  "--ct" |"--childtickets") CHILDTICKETS=1 ;;
                      "-h" | "--help") helpme ; exit  ;;
                  "--datelink" | "-d") DATELINKS=1    ;;
                 "-a" | "--activate" ) ACTIVATE=1     ;;
                     "-t" | "--theme") THEME=1        ;;
                 "-e" | "--extension") parvalue=2     ;;
                                    *) SRC="$par"     ;;
    esac
done

# Make initial root login
${SUDO} echo

echo "STEP: Setting variables"

if [ "$ENVIRONMENT" != "production" ] ; then
  ACTIVATE=1
fi

# Read optional environment setup variables
if [ -a $ENV_PTH ] ; then
    source $ENV_PTH
fi

# Check the existance of required params
if [ -z $ROOT ] ; then
    echo "Parameter \$ROOT (pointing to directory where installation exists) is missing, please set it first."
    exit -1
fi

# Create directory structure
${SUDO} mkdir -p $ROOT/trac
${SUDO} mkdir -p $ROOT/trac/dist
${SUDO} mkdir -p $ROOT/trac/logs
${SUDO} mkdir -p $ROOT/trac/config
${SUDO} mkdir -p $ROOT/trac/trac-htdocs
${SUDO} mkdir -p $ROOT/trac/themes
${SUDO} mkdir -p $ROOT/trac/projects
${SUDO} mkdir -p $ROOT/trac/webdav
${SUDO} mkdir -p $ROOT/trac/repositories
${SUDO} mkdir -p $ROOT/trac/archives
${SUDO} mkdir -p $ROOT/trac/results
${SUDO} mkdir -p $ROOT/trac/analytics

# Storage root point
trac="${ROOT}/trac"

#install root point
if [ -z "$SRC" ] ; then
  install="$(pwd)"
elif [ -n "$SRC" ] && [ -d "$SRC" ] ; then
  cd $SRC
  install="$(pwd)"
else
  install="${ROOT}/install/CQDE"
fi

# Distributions directory
dists="${trac}/dist"

${SUDO} chgrp devel -R ${install}/*
${SUDO} chmod g+w -R ${install}/plugins
${SUDO} chmod g+w -R ${install}/themes

# Distribution directory to be installed
if [ ${DATELINKS} -eq 1 ] ; then
  dist="${dists}/`date +%Y%m%d`"
else
  dist="${dists}/`date +%Y%m%d%H%M%S`"
fi
echo "     source root : ${install}"
echo "   projects root : ${trac}"
echo "      dists root : ${dists}"
echo "    current dist : ${dist}"
if [ "$ENVIRONMENT" == "production" ] ; then
echo "      enviroment : using production rules"
else
echo "      enviroment : using development rules"
fi

printf "\n02. Enabled features\n"
if [ $BATCHMODIFY -eq 1 ] ; then
  echo "   [x] BatchModify"
else
  echo "   [ ] BatchModify"
fi
if [ $CHILDTICKETS -eq 1 ] ; then
  echo "   [x] Child tickets"
else
  echo "   [ ] Child tickets"
fi
if [ $DATELINKS -eq 1 ] ; then
  echo "   [x] Date links"
else
  echo "   [ ] Date links"
fi
if [ $ACTIVATE -eq 1 ] ; then
  echo "   [x] Activate latest installation"
else
  echo "   [ ] Activate latest installation"
fi

printf "\nSTEP: Creating path for current dist\n"

if [ -x "${dist}" ]  && [ -x "${dist}/egg" ] ; then
  ${SUDO} rm -rf ${dist}/*
fi

${SUDO} mkdir -p ${dist}
if [ ! $? -eq 0 ] ; then
  printf "\nerror: Cannot create dist directory\n"
  exit 2
fi

${SUDO} chgrp devel ${dist}
${SUDO} mkdir ${dist}/egg
${SUDO} mkdir ${dist}/scripts
${SUDO} rm -rf /tmp/cqde
mkdir -p /tmp/cqde

printf "\nSTEP: Unzipping eggs\n"

for ext in `echo $EXTENSIONS` ; do
  ${SUDO} unzip -q ${install}/plugins/${ext}-*.egg -d ${dist}/egg/$ext.egg
  printf "${dist}/egg/$ext.egg\n" >> /tmp/cqde/dist.pth
done

if [ $BATCHMODIFY -eq 1 ] ; then
  ${SUDO} unzip -q ${install}/plugins/BatchModify-*.egg -d ${dist}/egg/BatchModify.egg
  printf "${dist}/egg/BatchModify.egg\n" >> /tmp/cqde/dist.pth
fi

if [ $CHILDTICKETS -eq 1 ] ; then
  ${SUDO} unzip -q ${install}/plugins/Tracchildtickets-*.egg -d ${dist}/egg/Tracchildtickets.egg
  printf "${dist}/egg/Tracchildtickets.egg\n" >> /tmp/cqde/dist.pth
fi

${SUDO} cp /tmp/cqde/dist.pth ${dist}/dist.pth

printf "\nSTEP: Distribution actions\n"

if [ $ACTIVATE -eq 1 ] ; then
  echo " * Activating"
  ${SUDO} rm ${dists}/current ; ${SUDO} ln -s ${dist} ${dists}/current
else
  echo " * Not activated!. Activate distribution by manually using activate.sh script"
fi

${SUDO} mkdir -p ${dist}/theme
if [  $THEME -eq 1 ] ; then
  printf "\nSTEP: Copy theme\n"
  ${SUDO} cp ${install}/themes/default/* ${dist}/theme -R
fi

printf "\nSTEP: Copy cron scripts\n"
${SUDO} cp ${install}/scripts/cron/* ${dist}/scripts/ -R
${SUDO} cp ${install}/scripts/hooks/* ${dist}/scripts/ -R

printf "\nSTEP: Set file permissions\n"
${SUDO} chown -R ${WEBSRV_USER}:${WEBSRV_GROUP} ${dist}
${SUDO} chmod -R a+r ${dist}

printf "\nSTEP: Clean up\n"
${SUDO} rm ${install}/cqde/dist -rf
${SUDO} rm ${install}/multiproject/dist -rf
${SUDO} rm ${install}/plugins/*/dist -rf
${SUDO} rm -rf /tmp/cqde/
${SUDO} rm -f ${install}/installed_by_*
${SUDO} touch ${dist}/installed_by_${USER}_from_$(echo $HOSTNAME | awk -F\. '{ print $1 }')

printf "\nSTEP: Distribution successfully installed at: ${dist}\n"

printf "\nSTEP: New migrations\n"
migrationspy="${install}/scripts/update.py"
if [ -r ${migrationspy} ] ; then
  echo -e "$(python ${migrationspy} | grep ': [0-9]' | tail -5 | grep -i '^new'| sed 's/^new  /\\033[40m\\033[33m NEW \\033[0m/g' | awk -F\: '{ print "  "$1" "$2 }')"
else
  printf "\n ERROR: Cannot find migrationspy"
fi
printf "\n"
