from trac.core import Component, implements
from trac.web.api import IRequestFilter

from multiproject.core.analytics.event import EventLogIO

class RequestAnalytics(Component):
    implements(IRequestFilter)

    ignore_list = ['/health', '/usericon']
    prefix_ignore_list = ['/chrome', '/res/']
    suffix_ignore_list = ['.css', '.js', '.png', '.gif', '.jpg']

    def __init__(self):
        self.env_name = self.env.project_identifier

    def pre_process_request(self, req, handler):
        # If request is applicable (not in ignore list)
        # Write page_request in event log
        if self.is_applicable(req):
            event = {}
            event['event'] = 'page_request'
            event['project'] = self.env_name
            event['username'] = req.authname
            event['method'] = req.method
            event['path_info'] = req.path_info

            log = EventLogIO()
            log.write_event(event)
        return handler

    def post_process_request(self, req, template, data, content_type):
        """ No need for changes here """
        return template, data, content_type

    def is_applicable(self, req):
        if req.path_info in self.ignore_list:
            return False

        for prefix in self.prefix_ignore_list:
            if req.path_info.startswith(prefix):
                return False

        for suffix in self.suffix_ignore_list:
            if req.path_info.endswith(suffix):
                return False

        return True
