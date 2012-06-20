# -*- coding: utf-8 -*-
from trac.admin.api import IAdminPanelProvider
from trac.core import Component, implements
from trac.perm import PermissionSystem
from trac.util.translation import _
from trac.web.chrome import add_notice, add_warning

from multiproject.core.permissions import CQDEUserGroupStore
from multiproject.core.configuration import conf

from multiproject.common.environment import TracEnvironment


class GroupPermissionAdminPanel(Component):
    implements(IAdminPanelProvider)

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if 'PERMISSION_GRANT' in req.perm or 'PERMISSION_REVOKE' in req.perm:
            yield ('permissions', _('Permissions'), 'groupspermissions', _('Groups'))

    def render_admin_panel(self, req, cat, page, path_info):
        self.groupstore = CQDEUserGroupStore(self._get_environment_id())

        if req.method == 'POST':
            if req.args.get('add'):
                self.add_permission_to_group(req)
            elif req.args.get('remove'):
                if req.args.get('permremovelist'):
                    self.remove_permission_from_group(req)
                if req.args.get('groupremovelist'):
                    self.remove_groups(req)

        all_permissions = self._get_all_permissions()
        all_group_permissions = self.groupstore.get_all_group_permissions()
        group_users = self.groupstore.get_user_count_from_groups()
        domain_name = conf.domain_name

        return 'admin_grouppermissions.html', {
            'available_permissions' : all_permissions,
            'group_permissions' : all_group_permissions,
            'group_users' : group_users,
            'domain_name' : domain_name
            }

    def add_permission_to_group(self, req):
        req.perm.require('PERMISSION_GRANT')
        group = req.args.get('group', '').strip()
        permission = req.args.get('permission', '').strip()

        if not group or not permission or permission not in self._get_all_permissions():
            return

        if not self.groupstore.can_grant_permission_to_group(group, permission):
            add_warning(req, "Can't give that permission for anonymous.")
            return

        req.perm.require(permission)
        if self.groupstore.grant_permission_to_group(group, permission):
            add_notice(req, _('The group %(where)s has been granted the permission %(what)s.',
                              where = group, what = permission))
        else:
            add_warning(req, _('The permission %(what)s cannot be granted to group %(where)s.',
                               what = permission, where = group))

    def remove_permission_from_group(self, req):
        req.perm.require('PERMISSION_REVOKE')
        selection = req.args.get('permremovelist')
        selection = self.__to_list(selection)
        for item in selection:
            if item:
                group, permission = item.rsplit('::', 1)
                if self.groupstore.revoke_permission_from_group(group, permission):
                    add_notice(req, _('The permission %(what)s has been revoked from %(where)s.',
                                    what = permission, where = group))
                else:
                    add_warning(req, _('The permission %(what)s cannot be revoked from %(where)s.',
                                    what = permission, where = group))

    def remove_groups(self, req):
        req.perm.require('PERMISSION_REVOKE')
        selection = req.args.get('groupremovelist')
        selection = self.__to_list(selection)
        for group in selection:
            if self.groupstore.remove_group(group):
                add_notice(req, _('The group %(what)s has been removed.', what = group))
            else:
                add_warning(req, _('The group %(what)s cannot be removed.', what = group))

    def _get_environment_id(self):
        environment = TracEnvironment.read(conf.resolveProjectName(self.env))
        return environment.environment_id

    def _get_all_permissions(self):
        perm = PermissionSystem(self.env)
        return perm.get_actions()

    def __to_list(self, selection):
        return isinstance(selection, list) and selection or [selection]
