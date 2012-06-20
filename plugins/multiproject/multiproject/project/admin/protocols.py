# -*- coding: utf-8 -*-
from trac.core import Component, implements, TracError
from trac.admin.api import IAdminPanelProvider

from multiproject.common.projects import Projects
from multiproject.core.configuration import conf

from multiproject.core.proto import ProtocolManager
from trac.web.chrome import add_warning, add_notice

class ProtocolAdminPanel(Component):
    """ Trac admin panel component for selecting
        allowed storage access protocols
    """
    implements(IAdminPanelProvider)

    def __init__(self):
        projects_api = Projects()
        self.project_identifier = conf.resolveProjectName(self.env)
        self.project_id = projects_api.get_project_id(self.project_identifier)
        self.protos = ProtocolManager(self.project_id)
        self.scm_type = self.env.config.get('trac', 'repository_type')
        self.available_scm_schemes = ProtocolManager.available_schemes(self.scm_type)
        self.available_dav_schemes = ProtocolManager.available_schemes('dav')
        self._init_allowed_schemes()

    def _init_allowed_schemes(self):
        try:
            self.allowed_scm_schemes = self.protos.allowed_protocols(self.scm_type)
            self.allowed_dav_schemes = self.protos.allowed_protocols('dav')
        except:
            raise TracError("Server error. Try again later.")

    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield ('general', 'General', 'protocol', 'Protocols')

    def render_admin_panel(self, req, cat, page, path_info):
        req.perm.require('TRAC_ADMIN')

        if req.method == 'POST':
            self._process_changes(req)
        return self._show_panel(req)

    def _process_changes(self, req):
        scm_protos = dav_protos = set([])

        if 'scm_proto' in req.args:
            scm_protos = set(self.__to_list(req.args['scm_proto']))
        if 'dav_proto' in req.args:
            dav_protos = set(self.__to_list(req.args['dav_proto']))

        if not self._validate(scm_protos, dav_protos):
            msg = 'Changes not stored, make sure that at least one protocol for each ' \
                  'section is selected. If you want to disable any section, configure ' \
                  'the appropriate permissions in the "Groups" page'
            add_warning(req, msg)
            return

        scm_protos_to_disallow = self.allowed_scm_schemes - scm_protos
        dav_protos_to_disallow = self.allowed_dav_schemes - dav_protos
        scm_protos_to_allow = scm_protos - self.allowed_scm_schemes
        dav_protos_to_allow = dav_protos - self.allowed_dav_schemes

        try:
            # Change scm protocols
            self.protos.disallow_protocols(scm_protos_to_disallow, self.scm_type)
            self.protos.allow_protocols(scm_protos_to_allow, self.scm_type)

            # Change dav protocols
            self.protos.disallow_protocols(dav_protos_to_disallow, 'dav')
            self.protos.allow_protocols(dav_protos_to_allow, 'dav')
        except:
            raise TracError("Server error. Try again later.")

        add_notice(req, "Changes saved")
        self._init_allowed_schemes()

    def _show_panel(self, req):
        data = {'available_scm_protocols':self.available_scm_schemes,
                'available_dav_protocols':self.available_dav_schemes,
                'allowed_scm_protocols':self.allowed_scm_schemes,
                'allowed_dav_protocols':self.allowed_dav_schemes,
                'protos':ProtocolManager.protocols.keys()} #@UndefinedVariable

        return 'admin_protocols.html', data

    def _validate(self, scm_protos, dav_protos):
        """ both arrays needs to have items
        """
        return scm_protos and dav_protos

    def __to_list(self, selection):
        """ Makes sure selection is a list
        """
        return isinstance(selection, list) and selection or [selection]
