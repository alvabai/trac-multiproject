from trac.core import Component, implements
from trac.wiki.api import IWikiChangeListener

from multiproject.core.analytics.event import EventLogIO


class WikiAnalytics(Component):
    """
    Adds analytics event writing for wiki events
    """

    implements(IWikiChangeListener)

    def __init__(self):
        self.env_name = self.env.path.split('/')[-1]

    def wiki_page_added(self, page):
        log = EventLogIO()
        event = {}
        event['event'] = "wiki_created"
        event['project'] = self.env_name
        event['username'] = page.author
        log.write_event(event)

    def wiki_page_changed(self, page, version, t, comment, author, ipnr):
        log = EventLogIO()
        event = {}
        event['event'] = "wiki_edited"
        event['project'] = self.env_name
        event['username'] = author
        log.write_event(event)

    def wiki_page_deleted(self, page):
        """
        We do not get history from deleted page
        nor author who deleted the page, so we
        need to skip this one :(
        """
        pass

    def wiki_page_version_deleted(self, page):
        pass

    def wiki_page_renamed(self, page, old_name):
        pass
