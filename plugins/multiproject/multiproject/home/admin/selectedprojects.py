# -*- coding: utf-8 -*-
from trac.core import Component, implements
from trac.admin.api import IAdminPanelProvider

from multiproject.common.projects import Projects
from multiproject.core.configuration import conf

class SelectedProjectsAdminPanel(Component):
    """ Trac admin panel component
    """
    implements(IAdminPanelProvider)

    # Part of IAdminPanelProvider interface
    def get_admin_panels(self, req):
        """ Introduce new item into admin navigation panel
        """
        if conf.resolveProjectName(self.env) == "home":
            if 'TRAC_ADMIN' in req.perm:
                yield ('projects', 'Projects', "selected", 'Featured projects')

    # Part of IAdminPanelProvider interface
    def render_admin_panel(self, req, cat, page, path_info):
        """ Renders updates admin panel page
        """
        req.perm.require('TRAC_ADMIN')

        api = Projects()
        selected = []

        if req.method == 'POST':
            if req.args.get('searchprojects'):
                selected = api.get_featured_projects()

                projectids = []
                for project in selected:
                    projectid = project['project_id']
                    projectids.append(projectid)

                rawsearch = api.search_project(req.args.get('pattern'), None, 1, 50)

                for project in rawsearch:
                    if not project['project_id'] in projectids:
                        project['priority'] = None
                        selected += tuple([project])

            elif req.args.get('update'):
                selection = req.args.get('projects')
                selection = self.__to_list(selection)
                projects = []

                for project in selection:
                    value = req.args.get(project)
                    if value is not None and value != "remove":
                        projects.append((project, value))

                api.update_featured_projects(projects)
                selected = api.get_featured_projects()
        else:
            selected = api.get_featured_projects()

        return 'admin_selected_projects.html', { 'selected': selected,
                                                 'maxvalue': 20 }

    def __to_list(self, selection):
        return isinstance(selection, list) and selection or [selection]
