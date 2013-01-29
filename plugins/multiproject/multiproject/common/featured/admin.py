# -*- coding: utf-8 -*-
"""
Module contains the admin interface for featured projects
"""
from trac.core import Component, implements
from trac.admin.api import IAdminPanelProvider

from multiproject.common.projects import Projects
from multiproject.core.configuration import conf

class FeaturedProjectsAdminPanel(Component):
    implements(IAdminPanelProvider)

    # IAdminPanelProvider methods

    def get_admin_panels(self, req):
        """
        Introduce new item into admin navigation panel
        """
        if 'TRAC_ADMIN' in req.perm:
            yield ('projects', 'Projects', "featured", 'Featured')

    def render_admin_panel(self, req, cat, page, path_info):
        """
        Renders updates admin panel page
        """
        req.perm.require('TRAC_ADMIN')

        papi = Projects()
        selected = []

        if req.method == 'POST':
            if req.args.get('searchprojects'):
                selected = papi.get_featured_projects()
                projectids = []
                for project in selected:
                    projectid = project.id
                    projectids.append(projectid)

                rawsearch = papi.search_project(req.args.get('pattern'), None, 1, 50)

                for project in rawsearch:
                    if not project.id in projectids:
                        project.priority = None
                        selected.append(project)

            elif req.args.get('update'):
                selection = req.args.get('projects')
                selection = isinstance(selection, list) and selection or [selection]
                projects = []

                for project in selection:
                    value = req.args.get(project)
                    if value is not None and value != "remove":
                        projects.append((project, value))

                papi.update_featured_projects(projects)
                selected = papi.get_featured_projects()
        else:
            selected = papi.get_featured_projects()

        data = {
            'selected': selected,
            'maxvalue': 20
        }
        return 'multiproject_featured_admin.html', data