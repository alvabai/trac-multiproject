# -*- coding: utf-8 -*-
import os
from urlparse import urlparse

from multiproject.core.auth.basic_access import BasicAccessControl
from multiproject.core.timeline import TimelineEvent
from multiproject.core.configuration import conf


class DAVAccessControl(BasicAccessControl):
    # Constants
    # For more details See. http://www.webdav.org/specs/rfc4918.html
    DAV_READ_METHODS = ['HEAD', 'GET', 'OPTIONS', 'PROPFIND', 'REPORT']
    # The following are not listed: 'LOCK', 'UNLOCK', 'PROPPATCH', 'POST'
    DAV_FILE_METHODS = ['PUT', 'DELETE', 'MOVE', 'MKCOL', 'COPY']
    DAV_DESTINATION_METHODS = ['MOVE', 'COPY']

    def __init__(self, req):
        BasicAccessControl.__init__(self, req)
        self.req = req
        self.method = req.method
        self._destination_path = None
        self._identifier = None
        self.url_dav_path = conf.url_dav_path.rstrip('/')

    def environment_identifier(self):
        # PythonOption project projectname
        # Parametrization for special cases
        if self._identifier:
            return self._identifier

        if 'project' in self.options:
            self._identifier = self.options['project']
        else:
            # Try from uri
            self._identifier = self.parse_identifier_from_uri()

        return self._identifier

    def destination_path_ok(self):
        if self.method in DAVAccessControl.DAV_DESTINATION_METHODS:
            parts = self.destination_path().split('/')
            # TODO: Fix this to use self.url_dav_path
            if len(parts) < 3 or not parts[2]:
                return False
            # Copying from one project to another is NOT ok
            if parts[2] != self.environment_identifier():
                return False

        return True

    def destination_path(self):
        if self._destination_path is not None:
            return self._destination_path
        self._destination_path = ''
        destination = self.req.headers_in.get('Destination')
        if not destination and hasattr(self.req, 'main'):
            # If req is a sub-request, req.main is the main request.
            destination = self.req.main.headers_in.get('Destination')

        if destination:
            # Parse path from url
            destination = urlparse(destination).path
            # Checks:
            # - Don't allow '..' in path (additional check).
            # - destination path must start with conf.url_dav_path + '/'
            if not '..' in destination:
                if destination.startswith(self.url_dav_path + '/'):
                    # Normalize from double slashes (since .. cannot be there)
                    self._destination_path = os.path.normpath(destination)
                else:
                    conf.log.warning('webdav: Destination_path was not starting with "%s": %s' %
                                     (self.url_dav_path + '/', destination))
            else:
                conf.log.info('webdav: Destination_path must not contain "..": %s' % destination)
        return self._destination_path

    def is_read(self):
        """ True read, False write
        """
        return self.method in self.DAV_READ_METHODS

    def read_action(self):
        return 'WEBDAV_VIEW'

    def write_action(self):
        return 'WEBDAV'

    def post_permission_check_hooks(self):
        """
        Insert event in timeline
        """
        identifier = self.environment_identifier()
        if self.method in self.DAV_FILE_METHODS and identifier:
            if self.method in DAVAccessControl.DAV_DESTINATION_METHODS:
                TimelineEvent(identifier, self.username).webdav_event(self.req,
                    destination_path=self.destination_path())
            else:
                TimelineEvent(identifier, self.username).webdav_event(self.req)
