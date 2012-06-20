# -*- coding: utf-8 -*-
from trac.core import Component, implements
from trac.admin.api import IAdminPanelProvider

from multiproject.common.projects import Projects
from multiproject.core.configuration import conf
from multiproject.core.cache.project_cache import ProjectCache


class ProjectIconAdminPanel(Component):
    """ Trac admin panel component for project icon
    """
    implements(IAdminPanelProvider)

    def get_admin_panels(self, req):
        """ Admin panel navigation items
        """
        if 'TRAC_ADMIN' in req.perm:
            yield ('general', 'General', 'projecticon', 'Project Icon')

    # IAdminPanelProvider interface requirement
    def render_admin_panel(self, req, cat, page, path_info):
        """ Renders categorization admin panel
        """
        req.perm.require('TRAC_ADMIN')

        papi = Projects()

        project = papi.get_project(env_name = conf.resolveProjectName(self.env))

        if req.method == 'POST':
            if 'removeicon' in req.args:
                project.createIcon(None)
            elif 'icon' in req.args:
                project.createIcon(req.args.get('icon'))

            cache = ProjectCache.instance()
            cache.clearProject(project.id)
            cache.clearProjectIcon(project.id)

        data = {}
        data['env'] = req.base_path
        data['project_id'] = project.id
        data['icon_id'] = project.icon_id
        return 'admin_project_icon.html', data
