# -*- coding: utf-8 -*-
"""
Watchlist notifier. Reads all project watchers and sends them emails about
time line events in the projects they watch.

.. NOTE::

    The module methods are heavy. Do not use these in requests unless
    planning on making them slow on purpose.
"""
from trac.util.html import plaintext

from multiproject.common.projects import Project
from multiproject.core.users import get_userstore
from multiproject.core.util import to_web_time
from multiproject.core.watchlist import CQDEWatchlistStore
from multiproject.common.notifications.email import EmailNotifier
from multiproject.home.watchlist.watchlist_events import WatchlistEvents


class WatchlistNotifier(object):
    """
    The actual implementation of notifier. Usage::

        from multiproject.home.watchlist.watchlist_notifier import WatchlistNotifier

        conf = Configuration.instance()
        module = WatchlistNotifier(Environment('/path/to/projectx'))
        module.notify_now(watchlist_type)
    """
    def __init__(self, env):
        """
        :param Environment env: The trac Environment() object.
        """
        self.env = env

    def notify_now(self, notification_frequency):
        """
        Send notification email to project watchers.

        :param str notification_frequency: The notification frequency, used to fetch
            users which have something on that watchlist.
        """
        store = CQDEWatchlistStore()
        watches = store.get_by_notification(notification_frequency)

        notifylist = {}
        for w in watches:
            if notifylist.get(w.project_id) is None:
                notifylist[w.project_id] = []
            notifylist[w.project_id].append(w.user_id)

        userstore = get_userstore()

        counter = 0
        for project_id in notifylist.keys():
            project = Project.get(id=project_id)

            # Get all events for this project
            events = self._get_project_events(project, notification_frequency)

            # Send one email per user, because everyone may have a different
            # set of permissions (i.e. which events he/she has permission to see)
            for user_id in notifylist[project_id]:
                user = userstore.getUserWhereId(user_id)
                if user:
                    # filter eventlist by user's permissions
                    filtered_events = WatchlistEvents(self.env).filter_events(events, user, project)
                    if filtered_events:
                        addresses = [user.mail]
                        message = self._format_message(user, project, filtered_events)
                        title = "Project updated: %s" % project.env_name
                        mail = EmailNotifier(self.env, subject=title, data={'body':message})
                        mail.notify_emails(addresses)
                        self.env.log.debug('Sent email notification to: %s' % user)
                        counter += 1
                    else:
                        if notification_frequency != 'immediate':
                            self.env.log.debug('No events to sent to %s about %s' % (user, project))
                else:
                    self.env.log.warning('User %d in notification list was not found in userstore' % user_id)

        # Log the results
        self.env.log.info('Sent %s watchlist notifications (%s)' % (counter, notification_frequency))


    def _get_project_events(self, project, notification_frequency):
        """ List all events in project that happened in a given time span
        """
        time = {
            'immediate': (0, 5), # (days, minutes)
            'daily': (1, 0),
            'weekly': (7, 0)
        }
        return WatchlistEvents(self.env).get_project_events(project,
            days=time[notification_frequency][0],
            minutes=time[notification_frequency][1])

    def _format_message(self, user, project, events):
        """
        Create the text body for email
        """
        url_home = self.env.config.get('multiproject', 'url_home').rstrip('/')
        url_service = self.env.config.get('multiproject', 'url_service').rstrip('/')

        # TODO: Move into template
        msg = "Hi %s,\nhere are the latest updates for the project %s that you are following.\n" % (
        user.username, project.project_name)

        for project, event, context in events:
            event_title = plaintext(event['render']('title', context), keeplinebreaks=False)
            description = self._get_event_description(event, context)
            date = to_web_time(event['date'])
            author = event['author']
            event_url = url_service + str(event['render']('url', context))

            msg += "\n%s\n" % event_title
            if description:
                msg += "%s\n" % description
            msg += "%s by %s\n" % (date, author)
            msg += "Read more about this at %s\n" % event_url

        prefs = url_home + "/prefs/following"
        msg += "\nYou are receiving this e-mail because you subscribed to this project. "
        msg += "You may edit the frequency or stop following this project at %s.\n" % prefs
        return msg

    def _get_event_description(self, event, context):
        if event['kind'] == 'wiki':
            return None
        description = plaintext(event['render']('description', context), keeplinebreaks=False)
        if len(description) > 70:
            description = description[:70] + "..."
        return description
