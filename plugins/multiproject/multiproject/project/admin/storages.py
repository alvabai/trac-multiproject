# -*- coding: utf-8 -*-
from pkg_resources import resource_filename #@UnresolvedImport

from trac.core import Component, implements
from trac.web.chrome import ITemplateProvider
from trac.admin.api import IAdminPanelProvider

from multiproject.common.projects import Projects
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

        env_name = self.env.path.split('/')[-1]
        project = Projects().get_project(env_name = env_name)
        vcs_type = conf.getVersionControlType(env_name) # TODO: deprecate / heavy call!
        vcs_url = project.get_repository_url()

        data = {}
        data['vcs_name'] = conf.getVersionControlName(vcs_type)
        data['vcs_type'] = vcs_type
        data['vcs_url'] = vcs_url
        data['dav_url'] = project.get_dav_url()
        data['vcs_cmd'] = 'clone'

        if vcs_type == "svn":
            data['vcs_cmd'] = 'checkout'

        return 'storages.html', data

    # ITemplateProvider methods
    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        return []
