"""
Watchlist module provides a support for users to follow other projects. When the user follows another project,
he/she can see the latest changes per project on home -project homepage.

Watchlist timeline:
    Lists last project activity within 7 days. URL: /home/watchlist_timeline


User preferences:
    User can see and modify the list of followed projects in user preferences.
    Implementation exists in :class:`multiproject.common.users.prefs_watchlist.WatchlistPreferencePanel`

Project following macro:
    Plugin comes with the macro: ``[[WatchProject]]`` that will provide a block for project following.
    It is implemented in :class:`multiproject.project.summary.watch.WatchProjectsModule`

.. NOTE::

    Project following modules should be all be moved into one location, preferably ``multiproject.following``:

Technical notes
===============

- ProjectTimelineEvents introduces a new extension point: ITimelineEventProvider.

"""

from watchlist_timeline import *
from watchlist_notifier import *
from watchlist_events import *
