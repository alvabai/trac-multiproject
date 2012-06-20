# -*- coding: utf-8 -*-
"""
Module provides the UI for listing archived projects, restoring them or removing completely.
"""
from trac.core import Component, implements
from trac.util.translation import _
from trac.admin.api import IAdminPanelProvider
from trac.web.chrome import add_notice, add_warning, add_script

from multiproject.common.projects.archive import ProjectArchive


class ProjectArchiveAdmin(Component):
    implements(IAdminPanelProvider)

    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield ('projects', _('Projects'), 'prjarchive', _('Project archive'))

    def render_admin_panel(self, req, cat, page, path_info):
        req.perm.require("TRAC_ADMIN")
        arch = ProjectArchive()
        projects = arch.list()

        if req.method == 'POST':
            archived_project_id = int(req.args.get('archived_project_id', 0))
            action = req.args.get('action', 'noop')

            try:
                if action == 'restore':
                    if arch.restore(archived_project_id, self.env):
                        add_notice(req, _('Restored project successfully'))

                elif action == 'remove':
                    if arch.remove(archived_project_id):
                        add_notice(req, _('Removed project successfully'))

                elif action == 'remove_expired':
                    if arch.remove_expired():
                        add_notice(req, _('Removed expired projects successfully'))

                else:
                    add_warning(req, _('Unknown action'))

            except Exception:
                add_warning(req, _('Failed to complete the action'))
                self.log.exception('Failed to {0} for project {1}'.format(action, archived_project_id))

            # After post method, redirect back to listing
            return req.redirect(req.href('/admin/projects/prjarchive'))

        add_script(req, 'multiproject/js/multiproject.js')
        add_script(req, 'multiproject/js/admin_project_archive.js')
        return 'multiproject_admin_project_archive.html', {'projects': projects}
