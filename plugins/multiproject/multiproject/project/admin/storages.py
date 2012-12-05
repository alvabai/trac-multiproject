# -*- coding: utf-8 -*-
from pkg_resources import resource_filename

from trac.core import Component, implements
from trac.web.chrome import ITemplateProvider
from trac.admin.api import IAdminPanelProvider

from multiproject.common.projects import Project
from multiproject.core.configuration import conf


class StoragesAdminPanel(Component):
    """ Trac admin panel component
    """
    implements(IAdminPanelProvider, ITemplateProvider)

    # Part of IAdminPanelProvider interface
    def get_admin_panels(self, req):
        """ Introduce new item into admin navigation panel
        """
        if 'TRAC_ADMIN' in req.perm:
            yield ('general', 'General', 'storages', 'Storages')

    # Part of IAdminPanelProvider interface
    def render_admin_panel(self, req, cat, page, path_info):
        """ Renders storage admin panel page
        """
        req.perm.require('TRAC_ADMIN')

        project = Project.get(self.env)
        vcs_type = conf.getVersionControlType(self.env.project_identifier)  # TODO: deprecate / heavy call!
        vcs_url = project.get_repository_url()

        data = {'vcs_name': conf.getVersionControlName(vcs_type),
                'vcs_type': vcs_type,
                'vcs_url': vcs_url,
                'dav_url': project.get_dav_url(),
                'vcs_cmd': 'clone'}

        if vcs_type == "svn":
            data['vcs_cmd'] = 'checkout'

        return 'storages.html', data

    # ITemplateProvider methods
    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        return []
