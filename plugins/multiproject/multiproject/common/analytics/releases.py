# -*- coding: utf-8 -*-
"""
Analytics event tracker for Trac downloads plugin. Listens to download created
and downloaded events from Trac downloads plugin and saves them to database.
"""
from trac.core import Component, implements

from multiproject.core.analytics.event import EventLogIO

try:
    from tracdownloads.api import IDownloadListener, IDownloadChangeListener

    class ReleaseAnalytics(Component):
        implements(IDownloadListener, IDownloadChangeListener)

        def __init__(self):
            self.env_name = self.env.project_identifier

        def download_created(self, context, download):
            log = EventLogIO()
            event = {}
            event['event'] = "release_uploaded"
            event['project'] = self.env_name
            event['username'] = context.req.authname
            log.write_event(event)

        def downloaded(self, context, download):
            """Called when a file is downloaded
            """
            log = EventLogIO()
            event = {}
            event['event'] = "release_downloaded"
            event['project'] = self.env_name
            event['username'] = context.req.authname
            log.write_event(event)

        # OUT OF ANALYTICS SCOPE
        def download_changed(self, context, download, old_download):
            """Called when a download is modified.
            `old_download` is a dictionary containing the previous values of the
            fields and `download` is a dictionary with new values. """

        def download_deleted(self, context, download):
            """Called when a download is deleted. `download` argument is
            a dictionary with values of fields of just deleted download."""

except ImportError:
    class ReleaseAnalytics(Component):
        pass
