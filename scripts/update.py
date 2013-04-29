#!/usr/bin/env python

"""
Provides database migration commandline interface
"""

import logging
import optparse

from multiproject.core.migration import MigrateMgr
from multiproject.core.configuration import Configuration


conf = Configuration.instance()


def main():
    logging.basicConfig(format='%(message)s')

    opt = optparse.OptionParser()
    opt.add_option('--update-to', '-t', default=None)
    opt.add_option('--update-new', '-u', action="store_true", default=False)
    opt.add_option('--cherry-pick-update', '-p',default=None)
    opt.add_option('--cherry-pick-downgrade', '-d', default=None)
    opt.add_option('--testdb', default=None)
    options, arguments = opt.parse_args()

    if options.testdb:
        Configuration.config_file = '/etc/trac/cqde.test.ini'
        conf.refresh()

    exec "from multiproject.core.migrations import *"
    param_was_given = True
    mgr = MigrateMgr.instance()
    if options.update_new:
        mgr.update_new()
    elif options.update_to:
        mgr.update_to(options.update_to)
    elif options.cherry_pick_update:
        mgr.cherry_pick(options.cherry_pick_update, True)
    elif options.cherry_pick_downgrade:
        mgr.cherry_pick(options.cherry_pick_downgrade, False)
    else:
        param_was_given = False
    mgr.show_status()

    if not param_was_given:
        print "\n\nTo install migrations, run:"
        print "    python update.py --update-new"
        print "        - Runs all new migration. Shorthand: -u"
        print "\nOther options are:"
        print "    --update-to=MIGRATION, -t=MIGRATION"
        print "        - Runs all migrations up or down to the given name"
        print "    --cherry-pick-update=MIGRATION, -p=MIGRATION"
        print "        - Tries to update one, single migration. Dangerous!"
        print "    --cherry-pick-downgrade=MIGRATION, -d=MIGRATION"
        print "        - Tries to downgrade one, single migration. Dangerous!"
        print "\nTo show just status"
        print "    python update.py"


if __name__ == '__main__':
    main()
