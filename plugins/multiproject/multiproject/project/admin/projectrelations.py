# -*- coding: utf-8 -*-
from trac.core import Component, implements
from trac.util.translation import _
from trac.admin.api import IAdminPanelProvider

from multiproject.common.projects import Project
from multiproject.core.configuration import conf
from trac.web.chrome import add_script


class ProjectForkingAdminPanel(Component):
    implements(IAdminPanelProvider)

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield ('general', _('General'), 'relations', _('Project relations'))

    def render_admin_panel(self, req, cat, page, path_info):
        req.perm.require('TRAC_ADMIN')

        project = Project.get(self.env)
        child_projects = project.get_child_projects()

        data = {
            '_project_': project,
            'parent_project': project.parent_project,
            'child_projects': child_projects,
            'home': conf.url_home_path
        }

        add_script(req, 'multiproject/js/admin_relations.js')
        return 'multiproject_admin_relations.html', data
