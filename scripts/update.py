#!/usr/bin/env python

"""
Provides database migration commandline interface
"""

import logging
import optparse

from multiproject.core.migration import MigrateMgr
from multiproject.core.configuration import conf, Configuration


def main():
    logging.basicConfig(format='%(message)s')

    opt = optparse.OptionParser()
    opt.add_option('--update', '-u', default=None)
    opt.add_option('--testdb', default=None)
    options, arguments = opt.parse_args()

    if options.testdb:
        Configuration.config_file = '/etc/trac/cqde.test.ini'
        conf.refresh()

    exec "from multiproject.core.migrations import *"
    mgr = MigrateMgr.instance()
    mgr.commandline_install(options.update)

    if options.update is None:
        print "\n\nTo install migrations"
        print "\tpython update.py --update=[NAME]\n"
        print "\tThis will run ALL migrations up or down to given name"
        print "\nTo show just status"
        print "\tpython update.py"


if __name__ == '__main__':
    main()
