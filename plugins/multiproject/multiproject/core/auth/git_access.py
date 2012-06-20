# -*- coding: utf-8 -*-
from multiproject.core.auth.basic_access import BasicAccessControl


class GITAccessControl(BasicAccessControl):
    def __init__(self, req):
        BasicAccessControl.__init__(self, req)
        self.req = req

    def environment_identifier(self):
        # PythonOption identifier projectname
        # Parametrization for special cases
        if 'project' in self.options:
            return self.options['project']

        # Try from uri
        identifier = self.parse_identifier_from_uri()
        identifier = identifier.split('.')[0]
        return identifier

    def is_read(self):
        if self.req.path_info.endswith("git-receive-pack"):
            return False

        if self.req.args:
            arguments = self.req.args.split("&")
            is_read = not 'service=git-receive-pack' in arguments
            return is_read

        return True

    def read_action(self):
        return 'VERSION_CONTROL_VIEW'

    def write_action(self):
        return 'VERSION_CONTROL'
