from trac.core import Component, implements
from trac.ticket.api import ITicketChangeListener

from multiproject.core.analytics.event import EventLogIO


class TicketAnalytics(Component):
    implements(ITicketChangeListener)

    def __init__(self):
        self.env_name = self.env.path.split('/')[-1]

    def ticket_created(self, ticket):
        event_log = EventLogIO()
        event = {}
        event['event'] = "ticket_created"
        event['project'] = self.env_name
        event['username'] = ticket['reporter']
        event_log.write_event(event)

    def ticket_changed(self, ticket, comment, author, old_values):
        if ticket['status'] == 'closed':
            event_log = EventLogIO()
            event = {}
            event['event'] = "ticket_closed"
            event['project'] = self.env_name
            event['username'] = ticket['author']
            event_log.write_event(event)

    def ticket_deleted(self, ticket):
        """
        Deleting tickets is really rare because it can be done
        only with trac-admin console tool.

        See trac.ticket.admin.TicketAdmin

        We do not need to gather statistics about this
        """
        pass
