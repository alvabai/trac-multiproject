#! /bin/env python

"""
This file is the main file of Fabric script. It includes the actual tasks from ``tasks`` module
and helper classes and functions from ``fablib`` module, located in ./scripts/fabric folder.

Usage
=====
- Install Fabric and other required modules with command::

    apt-get install python python-dev python-pip alien
    pip install Fabric stdeb requests

- Get help on usage with commands (run command in same folder with this file)::

    fab help
    fab -h
    fab -l
    fab -d <taskname>

- Example task executions::

    fab -R pielinen-oss system.show_status
    fab -R pielinen-oss-fe system.restart_apache
    fab -H pielinen-oss-fe1 dist.clean dist.build
    fab -H pielinen-oss-fe1 dist.build:compress=true,ext=true
    fab -H pielinen-oss-fe1 dist.deploy:package="../../dist/*.tar.gz"
    fab -H pielinen-oss-fe1 system.get_database:name=trac_admin

Configuration
=============
The setups, controlled by Fabric tasks, can be defined and configured using config file name ``fabfile.ini``
See fabfile.example.ini located in this directory. You can modify it directly or place it in some of following locations.
File is read in listed order:

- $FABFILEINI
- ~/.fabfile.ini
- /etc/fabfile.ini
- fabfile.ini

"""
import sys
import os

from fabric.api import *

# Import helpers and tasks
sys.path = [os.path.join(os.path.dirname(__file__), 'scripts/fabric')] + sys.path
from fablib.api import logger, init
from tasks import system, service, dist, distro, devel

# Initialize Fabric with optional configuration file
init()

@task
def help():
    """
    Shows help about script usage
    """
    help = '''
    Looking for help? Try following:

    - fab -l         : show available tasks
    - fab -d <task>  : show details instruction for specific task
    - fab --help     : show fabric help
    '''
    print help

    print 'Roles:'

    if not env.roledefs:
        print '  No roles where found. Please configure your fabfile.ini'

    # Print shorted list of roles
    for rname, rhosts in sorted(env.roledefs.iteritems(), key=lambda (k,v): (v,k)):
        print str('  %s : %s' % (rname.ljust(15), ', '.join(rhosts)))
