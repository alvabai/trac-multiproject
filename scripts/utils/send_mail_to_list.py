# -*- coding: utf-8 -*-

# TODO: Remove this script, and replace with trac-admin command

import sys
import time

from trac.env import Environment
from multiproject.common import Project

from multiproject.core.configuration import Configuration
from multiproject.common.notifications.email import EmailNotifier

conf = Configuration.instance()

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def main():
    if '-h' in sys.argv or '--help' in sys.argv:
        print "Usage: python send_mail_to_project_admins.py [--batch N] [--limit N] [--sleep N] [-n] [--env ENV] "
        sys.exit()
    from_batch = 0
    if '--batch' in sys.argv:
        from_batch_index = sys.argv.index('--batch')+1
        if len(sys.argv) > from_batch_index:
            from_batch = int(sys.argv[int(from_batch_index)])
        else:
            print "Usage: python send_mail_to_project_admins.py [--batch N] [--limit N] [--sleep N] [-n] [--env ENV] "
            print "       (--batch used incorrectly)"
            sys.exit()
    from_sleep = 5
    if '--sleep' in sys.argv:
        from_sleep_index = sys.argv.index('--sleep')+1
        if len(sys.argv) > from_sleep_index:
            from_sleep = int(sys.argv[int(from_sleep_index)])
        else:
            print "Usage: python send_mail_to_project_admins.py [--batch N] [--limit N] [--sleep N] [-n] [--env ENV] "
            print "       (--sleep used incorrectly)"
            sys.exit()
    total_batch_count = -1
    if '--limit' in sys.argv:
        from_limit_index = sys.argv.index('--limit')+1
        if len(sys.argv) > from_limit_index:
            total_batch_count = int(sys.argv[int(from_limit_index)])
        else:
            print "Usage: python send_mail_to_project_admins.py [--batch N] [--limit N] [--sleep N] [-n] [--env ENV] "
            print "       (--limit used incorrectly)"
            sys.exit()

    env_name = 'HelpAndSupport'
    if '--env' in sys.argv:
        env_index = sys.argv.index('--env')+1
        if len(sys.argv) > env_index:
            env_name = sys.argv[int(env_index)]
        else:
            print "Usage: python send_mail_to_project_admins.py [--batch N] [--limit N] [-n] [--env ENV] "
            print "       (--env used incorrectly)"
            sys.exit()

    debug_only = False
    if '-n' in sys.argv:
        debug_only = True

    header = ''
    message = ''
    with open('message.txt') as fd:
        message = fd.read()
    with open('subject.txt') as fd:
        lines = fd.read().splitlines()
        for line in lines:
            if line:
                header = line

    mailNotifier = EmailNotifier(Environment(conf.getEnvironmentSysPath(env_name)),
            header, message)

    print "header: '%s'" % header
    print "message:\n---\n'%s'\n---\n" % message
    print "debug?:%s"%debug_only

    with open('project_admins.txt') as fd:
        users = fd.read().splitlines()

        index = 0
        counter = 0
        sent_batch_count = 0
        for chunk in chunks(users, 5):
            counter += 1
            if from_batch <= counter and (total_batch_count == -1 or total_batch_count > sent_batch_count):
                print "sending batch %s, from %s to %s, emails: %s" % (counter, index+1, index+len(chunk), chunk)
                if not debug_only:
                    mailNotifier.notify(chunk)
                time.sleep(from_sleep)
                sent_batch_count += 1
            index += 5


if __name__ == '__main__':
    main()
