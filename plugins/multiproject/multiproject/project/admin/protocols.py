# -*- coding: utf-8 -*-
from trac.core import Component, implements, TracError
from trac.admin.api import IAdminPanelProvider
from trac.web.chrome import add_warning, add_notice

from multiproject.common.projects import Project
from multiproject.core.proto import ProtocolManager


class ProtocolAdminPanel(Component):
    """ Trac admin panel component for selecting
        allowed storage access protocols
    """
    implements(IAdminPanelProvider)

    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield ('general', 'General', 'protocol', 'Protocols')

    def render_admin_panel(self, req, cat, page, path_info):
        req.perm.require('TRAC_ADMIN')

        protos = ProtocolManager(Project.get(self.env).id)
        scm_type = self.env.config.get('trac', 'repository_type')

        if req.method == 'POST':
            self._process_changes(req, protos, scm_type)

        return self._show_panel(req, protos, scm_type)

    def _process_changes(self, req, protos, scm_type):
        scm_protos = dav_protos = set([])

        allowed_scm_schemes = protos.allowed_protocols(scm_type)
        allowed_dav_schemes = protos.allowed_protocols('dav')

        if 'scm_proto' in req.args:
            scm_protos = set(self._to_list(req.args['scm_proto']))
        if 'dav_proto' in req.args:
            dav_protos = set(self._to_list(req.args['dav_proto']))

        if not self._validate(scm_protos, dav_protos):
            msg = 'Changes not stored, make sure that at least one protocol for each ' \
                  'section is selected. If you want to disable any section, configure ' \
                  'the appropriate permissions in the "Groups" page'
            add_warning(req, msg)
            return

        try:
            # Change scm protocols
            protos.disallow_protocols(allowed_scm_schemes - scm_protos, scm_type)
            protos.allow_protocols(scm_protos - allowed_scm_schemes, scm_type)

            # Change dav protocols
            protos.disallow_protocols(allowed_dav_schemes - dav_protos, 'dav')
            protos.allow_protocols(dav_protos - allowed_dav_schemes, 'dav')
        except:
            raise TracError("Server error. Try again later.")

        add_notice(req, "Changes saved")

    def _show_panel(self, req, protos, scm_type):
        data = {'available_scm_protocols': ProtocolManager.available_schemes(scm_type),
                'available_dav_protocols': ProtocolManager.available_schemes('dav'),
                'allowed_scm_protocols': protos.allowed_protocols(scm_type),
                'allowed_dav_protocols': protos.allowed_protocols('dav'),
                'protos': ProtocolManager.protocols.keys()}

        return 'admin_protocols.html', data

    def _validate(self, scm_protos, dav_protos):
        """ both arrays needs to have items
        """
        return scm_protos and dav_protos

    def _to_list(self, selection):
        """ Makes sure selection is a list
        """
        return isinstance(selection, list) and selection or [selection]
