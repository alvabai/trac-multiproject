import json
import datetime

from trac.util import datefmt

from multiproject.core.db import analytical_transaction
from multiproject.core.configuration import conf
from multiproject.core.cache.timeline_cache import TimelineCache


def _notify_event_occurred(project_identifier, event_type):
    """ This function will notify / invoke actions about the
    fact that anything happened in a project

    For now implemented here. In the future could be extensible through some interface.
    """
    from multiproject.home.timeline.api import GlobalTimeline
    gtl = GlobalTimeline()
    now = datetime.datetime.now(datefmt.localtz)
    update = False
    filters = None

    # Two hours back should be more than enough and also take one
    # hour to the future to make absolute sure that event is not missed
    past = now - datetime.timedelta(hours = 2)

    # Previously, if files events were noticed, the whole cache was updated.
    # That seemed to be too heavy operation to clear all events when files tab is updated.
    # Let's just accept, that there might be broken links in global timeline cache.

    future = now + datetime.timedelta(hours = 1)
    gtl.refresh_project(project_identifier, past, future, filters, update)
    cache = TimelineCache()
    cache.clear()


class EventLogIO(object):
    """
    Provides API for writing events.

    .. NOTE:: After moving to database queue there's not much left in this class.
              Maybe get rid of completely ?
    """

    def write_event(self, event):
        """
        Write one event into database queue.
        Trigger notify event if `refresh_global_timeline` is enabled.

        :param dict event: Event data
        Example: {'timestamp': <datetime>, 'event': 'wiki_create',
                  'project': 'bestproject', 'username': 'joeuser', 'forum_id': '35'}
        """

        # use this server's datetime as timestamp, UTC
        curdate = datetime.datetime.utcnow()
        event['timestamp'] = curdate.isoformat()

        # generate JSON from dict
        json_data = json.dumps(event)

        with analytical_transaction() as cursor:
            cursor.execute('INSERT INTO `data_queue` (`data`) VALUES (%s)', json_data)

        # Refresh global timeline if needed
        is_home_env = event['project'] == 'home'
        is_page_view = event['event'] == 'page_request'
        is_enabled = conf.refresh_global_timeline
        if is_enabled and not (is_home_env or is_page_view):
            _notify_event_occurred(event['project'], event['event'])
