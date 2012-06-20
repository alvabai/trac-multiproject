from genshi.builder import tag

from trac.ticket.web_ui import TicketModule
from trac.util.translation import _
from trac.ticket.query import QueryModule

class QueryModuleInterceptor(QueryModule):
    """ Component for changing View Tickets to Tickets
    """
    def __init__(self):
        QueryModule.__init__(self, self.compmgr)
    
    def get_active_navigation_item(self, req):
        # This activates tickets tab
        return 'ticket'

    def get_navigation_items(self, req):
        """ Change "View Tickets" to "Tickets"
        """
        from trac.ticket.report import ReportModule
        if 'TICKET_VIEW' in req.perm and \
                not self.env.is_component_enabled(ReportModule):
            yield ('mainnav', 'ticket',
                   tag.a(_('Tickets'), href=req.href.query()))

class TicketModuleInterceptor(TicketModule):
    """ Component for hiding "New Ticket" tab
    """
    def __init__(self):
        TicketModule.__init__(self, self.compmgr)
    
    def get_active_navigation_item(self, req):
        # This activates tickets when on New Ticket page
        return 'ticket'

    def get_navigation_items(self, req):
        # This hides New Ticket tab
        return []