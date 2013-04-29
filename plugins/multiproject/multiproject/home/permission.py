from trac.core import Component, implements
from trac.web.api import IRequestFilter
from trac.perm import IPermissionRequestor
from multiproject.core.configuration import Configuration
conf = Configuration.instance()


class HomePermissionFilter(Component):
    implements(IRequestFilter, IPermissionRequestor)

    exclude_paths = ["/user", "/rss", "/health", "/res"]

    def pre_process_request(self, req, handler):
        # Do not require login for health check or login page
        if self._starts_with_one(req.path_info, self.exclude_paths):
            return handler
        if conf.allow_anonymous_frontpage and req.path_info in ["", "/"]:
            return handler

        req.perm.require('WELCOME_VIEW')
        return handler

    def post_process_request(self, req, template, data, content_type):
        """ This does nothing.. Interface just wants this..
        """
        return template, data, content_type

    def get_permission_actions(self):
        return ['WELCOME_VIEW']

    def _starts_with_one(self, string, string_items):
        """ Test if one of the items in string_items array
            starts with a needle
        """
        for item in string_items:
            if string.startswith(item):
                return True
        return False
