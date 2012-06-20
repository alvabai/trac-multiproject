# -*- coding: utf-8 -*-
from trac.core import Component, implements, ExtensionPoint
from trac.mimeview.api import Context
from trac.util.translation import _
from trac.admin.api import IAdminPanelProvider
from trac.web.api import Href, RequestDone
from trac.web.chrome import add_warning, add_script

from multiproject.common.projects import Projects
from multiproject.common.projects.archive import ProjectArchive
from multiproject.common.projects.listeners import IProjectChangeListener
from multiproject.core.configuration import conf


class SystemAdminPanel(Component):
    """
    Class introduces the system section in project admin view and implements
    the project removal.
    """
    implements(IAdminPanelProvider)
    homeurl = Href(conf.url_home_path)

    # Extension points
    project_change_listeners = ExtensionPoint(IProjectChangeListener)

    # IAdminPanelProvider methods

    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield ('general', _('General'), 'system', _('System'))

    def render_admin_panel(self, req, cat, page, path_info):
        """
        Returns the admin view and handles the form actions
        """
        req.perm.require('TRAC_ADMIN')

        projects = Projects()
        project = projects.get_project(env_name=conf.resolveProjectName(self.env))

        if req.method == 'POST':
            thisurl = Href(req.base_path)(req.path_info)
            context = Context.from_request(req)

            # Handle project remove
            if 'remove' in req.args:
                # Don't allow removing home
                if project.env_name == conf.sys_home_project_name:
                    add_warning(req, 'Cannot remove home project')
                    return req.redirect(thisurl)

                # Archive the project before removal
                archive = ProjectArchive()
                archived = archive.archive(project)

                if not archived:
                    add_warning(req, 'Could not archive project "%s". Will not remove the project' % project.project_name)
                    return req.redirect(thisurl)

                # Notify listeners. The project object still exists, but database does not
                for listener in self.project_change_listeners:
                    listener.project_archived(project)

                # Do the actual project removal
                if projects.remove_project(project):
                    # Notify listeners. The project object still exists, but database does not
                    for listener in self.project_change_listeners:
                        listener.project_deleted(project)

                    # NOTE: We no longer have project tables/session etc available
                    self.redirect_home(req)

                else:
                    add_warning(req, 'Could not remove project "%s". Try again later' % project.project_name)
                    return req.redirect(thisurl)

        add_script(req, 'multiproject/js/multiproject.js')
        add_script(req, 'multiproject/js/admin_system.js')

        # NOTE: Trac automatically puts 'project' dict in chrome thus it cannot be used
        data = {'multiproject': {
            'project':project,
            'home_url':conf.url_home_path
        }}
        return 'admin_system.html', data

    def redirect_home(self, req):
        """
        Redirect without session save (what Trac does). This is required when the project no longer exists

        :param Request req: Trac request
        """
        status = 303 if req.method == 'POST' else 302

        req.send_response(status)
        req.send_header('Location', SystemAdminPanel.homeurl())
        req.send_header('Content-Type', 'text/plain')
        req.send_header('Content-Length', 0)
        req.send_header('Pragma', 'no-cache')
        req.send_header('Cache-Control', 'no-cache')
        req.send_header('Expires', 'Fri, 01 Jan 1999 00:00:00 GMT')
        req.end_headers()
        raise RequestDone

