# -*- coding: utf-8 -*-
from mercurial.hgweb.hgweb_mod import perms
from mercurial import wireproto

from multiproject.core.auth.basic_access import BasicAccessControl
from multiproject.core.configuration import conf


class MercurialAccessControl(BasicAccessControl):
    def __init__(self, req):
        BasicAccessControl.__init__(self, req)
        self.req = req
        self.cmd = self._read_hg_cmd()

    def environment_identifier(self):
        # PythonOption project projectname
        # Parametrization for special cases
        if 'project' in self.options:
            return self.options['project']

        # Try from uri
        return self.parse_identifier_from_uri()

    def has_permission(self):
        # Must be a protocol request and correct privileges
        return self.is_protocol_request() and BasicAccessControl.has_permission(self)

    def is_protocol_request(self):
        """ Check that this is a hg wireproto request
            and not hgweb ui request
        """
        # Must have command
        if not self.cmd:
            return False

        # Command must be a protocol command
        if self.cmd not in wireproto.commands.keys():
            return False

        return True

    def is_read(self):
        # It's a read if it's unlisted in permission map or not push
        return self.cmd and (self.cmd not in perms or perms[self.cmd] != 'push')

    def _read_hg_cmd(self):
        """ Read hg command attribute from request parameters
        """
        if not self.req.args:
            return None

        cmd = None
        arguments = self.req.args.split("&")
        for arg in arguments:
            key, value = arg.split("=")
            if key == 'cmd':
                # Make sure we get command only once and write malicious attempts into log
                # Mark cmd to None, so that access is restricted
                if cmd is not None:
                    conf.log.error("Attempt of spoofing hg command by giving it\
                                    twice in %s by %s with %s" % (str(self.username),
                                                                  str(self.environment_identifier()),
                                                                  str(self.req.args)))
                    cmd = None
                    break

                cmd = value
        return cmd

    def read_action(self):
        return 'VERSION_CONTROL_VIEW'

    def write_action(self):
        return 'VERSION_CONTROL'
