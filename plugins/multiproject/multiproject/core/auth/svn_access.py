# -*- coding: utf-8 -*-
from multiproject.core.auth.dav_access import DAVAccessControl


class SVNAccessControl(DAVAccessControl):
    """ SVN uses DAV for authentication so we can
        utilize most of dav authentication code
    """
    def read_action(self):
        return 'VERSION_CONTROL_VIEW'

    def write_action(self):
        return 'VERSION_CONTROL'
