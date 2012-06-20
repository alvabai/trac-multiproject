# -*- coding: utf-8 -*-
"""
Watchlist notifier script for periodically sending emails to people, who are
"watching" a project.

Simple manual run would be to do:

>>> sudo ./watchlist_notify.py immediate

Typically this script would be a cron task.

Now eats all errors but logs them into error log. The script will still return
non-zero on failure, so site admins will still pester us. But they'll no
longer get the python stack dump, which is printed into error log.
"""
import sys

from trac.env import Environment

from multiproject.core.configuration import Configuration
from multiproject.home.watchlist.watchlist_notifier import WatchlistNotifier


def main(watchlist_type):
    """
    Creates the infamous Configuration object to dig out home project env and
    sends watchlist notifications to all users that have registered to them.

    :param str watchlist_type: immediate, daily or weekly notification.
    """
    try:
        conf = Configuration.instance()
        module = WatchlistNotifier()
        module.notify_now(Environment(conf.getEnvironmentSysPath(conf.sys_home_project_name)),
                          watchlist_type)
    except Exception, e:
        conf.log.exception("Failed to send watchlist messages")
        return str(e)


if __name__ == '__main__':
    """
    The actual execution of the script. Parses args and passes them to main function
    """
    arg = None
    if len(sys.argv) < 2:
        print "Usage: python watchlist_notify.py immediate|daily|weekly"
        sys.exit()

    for arg in sys.argv[1:]:
        if arg not in ("immediate", "daily", "weekly"):
            print "Usage: python watchlist_notify.py immediate|daily|weekly"
            sys.exit()

    sys.exit(main(arg))
