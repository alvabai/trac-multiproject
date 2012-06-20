"""
Watchlist module provides a support for users to follow other projects. When the user follows another project,
he/she can see the latest changes per project on home -project homepage.

Watchlist timeline:
    Lists last project activity within 7 days. URL: /home/watchlist_timeline


User preferences:
    User can see and modify the list of followed projects in user preferences.
    Implementation exists in :class:`WatchlistPreferencePanel`


Technical notes
===============

- Module adds new table `webdav_events` into each project. See ``multiproject/project/database/webdav_events_db1.py``
  for details about the columns
- ProjectTimelineEvents introduces a new extension point: ITimelineEventProvider.
- :class:`multiproject.project.timeline.TimelineInformer` implements the defined extension point for the projects.


"""

from watchlist_timeline import *
from watchlist_notifier import *
from watchlist_events import *
