# -*- coding: utf-8 -*-
"""
Module contains the admin interface for featured projects
"""
#from trac.admin.api import IAdminPanelProvider

from common.projects.projectsTest import ProjectsStub

class FeaturedProjectsAdminPanel(object):
    #implements(IAdminPanelProvider)

    def get_admin_panels(self, req):
        """
        Introduce new item into admin navigation panel
        """
        if 'TRAC_ADMIN' in req.perm:
            yield ('projects', 'Projects', "featured", 'Featured')

    def render_admin_panel(self, req, cat=None, page=None, path_info=None):
        """
        Renders updates admin panel page
        """
        req.perm.require('TRAC_ADMIN')

        papi = ProjectsStub()
        selected = []

        if req.method == 'POST':
            if req.args.get('searchprojects'):
                print("Jee jee testi2")
                selected = papi.get_featured_projects()
                projectids = []
                for project in selected:
                    projectid = project.id
                    projectids.append(projectid)
                rawsearch = papi.search_project(req.args.get("pattern"), None, 1, 50)

                for project in rawsearch:
                    if not project['project_id'] in projectids:
                        project['priority'] = None
                        selected += tuple([project])

            elif req.args.get('update'):
                selection = req.args.get('projects')
                #Return contents of selection if non empty or [][]
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
        #return 'multiproject_featured_admin.html', data
        return data