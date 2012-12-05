# -*- coding: utf-8 -*-
"""
This module provides a way to backup and restore the project state via admin web ui, per project.
User needs to have ``TRAC_ADMIN`` permissions to access the functionality.

.. NOTE::

    Templates used with the module are coming via :mod:`multiproject.common.admin.admintemplateprovider`

"""
import re

from trac.web.chrome import add_notice, add_warning, Chrome, add_script, add_stylesheet
from trac.web.href import Href
from trac.web.api import IRequestHandler
from trac.admin.api import IAdminPanelProvider
from trac.admin.web_ui import PluginAdminPanel
from trac.core import Component, implements, TracError
from trac.util.translation import _

from multiproject.common.projects.backup import ProjectBackup
from multiproject.common.projects import Project
from multiproject.core.configuration import conf
from multiproject.core.users import get_userstore


class BackupRestoreModule(Component):
    """
    Module implements the backup/restore web ui
    """
    implements(IAdminPanelProvider, IRequestHandler)

    # IAdminPanelProvider methods

    def get_admin_panels(self, req):
        """
        Return a list of available admin panels.

        The items returned by this function must be tuples of the form
        `(category, category_label, page, page_label)`.
        """
        if 'TRAC_ADMIN' in req.perm:
            yield ('general', _('General'), 'backup', _('Backup and restore'))

    def render_admin_panel(self, req, category, page, path_info):
        """
        Process a request for an admin panel.

        :Returns: A tuple of the form `(template, data)`,
        """
        # Ensure the user has project admin permissions
        req.perm.assert_permission('TRAC_ADMIN')

        backups = []
        backup_href = Href('%s/admin/general/backup' % req.base_path)

        # Load the user based on authname
        user = get_userstore().getUser(req.authname)

        # Get the current environment name
        env_name = conf.resolveProjectName(self.env)

        # Initiate ProjectBackup, containing the backup/restore implementation
        prj = Project.get(env_name=env_name)
        pb = ProjectBackup(prj)
        backups = pb.get_backups()

        # Do the backup
        if req.path_info.endswith('backup/backup') and req.method == 'POST':
            try:
                pb.backup(user_id=user.id, description=req.args.get('description'))
                add_notice(req, _('Backup created'))
            except TracError, e:
                add_warning(req, _('Backup failed: %s' % e))

            # Return back to default backup page
            return req.redirect(backup_href())

        # Do the restore. URL format: backup/[backupnum]/restore
        if req.path_info.endswith('restore') and req.method == 'POST':
            # Get the restore id from the URL: backup/<id>/restore
            result = re.search('backup/(?P<backupid>\d+)/restore', req.path_info, re.UNICODE)
            if result:
                try:
                    # Restore the selected database using ProjectBackup.
                    pb.restore(backup_id=long(result.group('backupid')), user_id=long(user.id))
                    add_notice(req, _('Restored the project backup successfully'))

                    return req.redirect(backup_href())

                except TracError, e:
                    add_warning(req, _('Restore failed: %s' % e))
            else:
                add_notice(req, _('Invalid request'))

        # Do the backup delete. URL format: backup/[backupnum]/delete
        if req.path_info.endswith('delete') and req.method == 'POST':
            # Get the restore id from the URL: backup/<id>/delete
            result = re.search('backup/(?P<backupid>\d+)/delete', req.path_info, re.UNICODE)
            if result:
                try:
                    backup_id = long(result.group('backupid'))
                    pb.delete(backup_id)
                    add_notice(req, _('Deleted the project backup successfully'))

                    return req.redirect(backup_href())

                except TracError, e:
                    add_warning(req, _('Backup deletion failed: %s' % e))
            else:
                add_notice(req, _('Invalid request'))

        # Just return the list of existing backups
        Chrome(self.env).add_textarea_grips(req)


        add_script(req, 'multiproject/js/jquery-ui.js')
        add_stylesheet(req, 'multiproject/css/jquery-ui.css')
        add_script(req, 'multiproject/js/multiproject.js')
        add_script(req, 'multiproject/js/admin_backup.js')

        return 'multiproject_admin_backup.html', {'backups': backups, 'backup_href':backup_href}

    # IRequestHandler methods

    def match_request(self, req):
        """
        Check if request matches with /admin/general/plugins
        and process it by removing the upload functionality
        """
        match =  re.match(r'\/admin\/general\/backup\/?\w?', req.path_info)

        return bool(match)

    def process_request(self, req):
        """
        Process the incoming request
        """
        req.perm.assert_permission('TRAC_ADMIN')

        if req.method() == 'GET':
            pass

        # Process with original handler
        return PluginAdminPanel._render_view(self, req)
