# -*- coding: utf-8 -*-
"""
Module extends the Trac permission policy and store:

- GlobalPermissionPolicy: Always use group based permissions
- GlobalPermissionStore: Store and maintain permissions in trac_admin database

Also, ``GlobalPermissionPolicy`` introduces new permissions:

User:
    - USER_ADMIN: Manage all users
    - USER_CREATE: Create new local users
    - USER_VIEW: View user listings (for management purposes)
    - USER_AUTHOR: Full permissions for own or authored users
    - USER_MODIFY: Manage own account
    - USER_DELETE: Delete own account

For developers, use following convention when checking the permissions::

    userstore = conf.getUserStore()
    user = userstore.getUserWhereId(resource.id)

    # Check if user has permission at all
    req.perm.require('USER_MODIFY')

    # Or as conditional check
    if 'USER_ADMIN' in req.perm:
        print "I can do anything!"

    # Check if user can modify specified user
    req.perm.require('USER_MODIFY', Resource('user', id=user.id))

    # Check if user can remove specified user
    req.perm.require('USER_REMOVE', Resource('user', id=user.id))

"""
from trac.core import Component, implements, ExtensionPoint
from trac.perm import IPermissionStore, IPermissionRequestor, IPermissionPolicy, PermissionCache
from trac.ticket import Ticket

from multiproject.common.projects import Project
from multiproject.core.configuration import Configuration
conf = Configuration.instance()
from multiproject.core.permissions import CQDEPermissionPolicy, CQDEPermissionStore
from multiproject.common.environment import TracEnvironment


class GlobalPermissionStore(Component):
    """ Global wrapper implementation of permission storage and simple group management.

        Actual permission store is implemented in multiproject.core.permissions

        This component uses the `permission` table in the database to store
        permissions.

        IPermissionStore defines store for permissions
    """
    implements(IPermissionStore)

    def get_user_permissions(self, username):
        """
        Retrieve the permissions for the given user and return them in a
        dictionary.

        The permissions are stored in the database as (username, action)
        records. There's simple support for groups by using lowercase names
        for the action column: such a record represents a group and not an
        actual permission, and declares that the user is part of that group.
        """
        store = self._get_store()
        return store.get_user_permissions(username)

    def get_users_with_permissions(self, permissions):
        """
        Retrieve a list of users that have any of the specified permissions

        Users are returned as a list of usernames.
        """
        store = self._get_store()
        return store.get_users_with_permissions(permissions)

    def get_all_permissions(self):
        """
        Return all permissions for all users.

        The permissions are returned as a list of (subject, action)
        formatted tuples.
        """
        return self._get_store().get_all_permissions()

    def grant_permission(self, username, action):
        """ Grants a user the permission to perform the specified action.
        """
        return self._get_store().grant_permission(username, action)

    def revoke_permission(self, username, action):
        """ Revokes a users' permission to perform the specified action.
        """
        return self._get_store().revoke_permission(username, action)

    def _get_store(self):
        """
        :returns: CQDEPermissionStore instance for current env
        """
        return CQDEPermissionStore(env=self.env)


class GlobalPermissionPolicy(Component):
    implements(IPermissionPolicy, IPermissionRequestor)

    def get_permission_actions(self):
        """ Define some new permissions atoms
        """
        return ['VERSION_CONTROL_VIEW', ('VERSION_CONTROL', ['VERSION_CONTROL_VIEW']),
                'ATTACHMENT_CREATE',
                'PERMISSION_GRANT', 'PERMISSION_REVOKE',
                'USER_CREATE', 'USER_VIEW', 'USER_AUTHOR', 'USER_MODIFY', 'USER_DELETE',
                ('USER_ADMIN', ['USER_CREATE', 'USER_VIEW', 'USER_MODIFY']),
                ('PERMISSION_ADMIN', ['PERMISSION_GRANT', 'PERMISSION_REVOKE'])]

    def check_permission(self, action, username, resource, perm):
        """
        Checks permissions - Actual checking is done on CQDEPermissionPolicy class
        """
        # FIXME: Dirty hack to screw ILegacyAttachmentPolicy.
        perm_maps = {
            'ATTACHMENT_CREATE': {
                'ticket': 'TICKET_APPEND',
                'wiki': 'WIKI_MODIFY',
                'milestone': 'MILESTONE_MODIFY',
                'discussion': 'DISCUSSION_ATTACH'
            },
            'ATTACHMENT_VIEW': {
                'ticket': 'TICKET_VIEW',
                'wiki': 'WIKI_VIEW',
                'milestone': 'MILESTONE_VIEW',
                'discussion': 'DISCUSSION_ATTACH'
            },
            'ATTACHMENT_DELETE': {
                'ticket': 'TICKET_ADMIN',
                'wiki': 'WIKI_DELETE',
                'milestone': 'MILESTONE_DELETE',
                'discussion': 'DISCUSSION_ATTACH'
            }
        }
        perm_map = perm_maps.get(action)
        if perm_map and resource and resource.realm == 'attachment':
            action = perm_map.get(resource.parent.realm)

        policy = CQDEPermissionPolicy(self.env)

        # Project context check
        if resource and resource.realm == 'project':
            # NOTE: Load project to get environment key required by check_permission
            # NOTE: Internal TracEnvironment cannot be used because env can be home, whereas project id is not
            project = Project.get(id=resource.id)
            if project and policy.check_permission(project.trac_environment_key, action, username):
                return True
            return False

        # Ticket authors should be able to edit their own tickets
        # (excluding 'anonymous')
        if username != 'anonymous' \
           and resource and resource.id and resource.realm == 'ticket' \
           and action in ('TICKET_CHGPROP', 'TICKET_EDIT_DESCRIPTION'):
            ticket = Ticket(self.env, int(resource.id))
            if ticket.exists and username == ticket['reporter']:
                return True

        # Load lightweight trac environment to get environment id, required by internal check_permission
        env_name = conf.resolveProjectName(self.env)
        environment = TracEnvironment.read(env_name)

        # Check permission using global permission policy and storage
        if not policy.check_permission(environment.environment_id, action, username):
            return False

        # Additional, resources based checks

        # User author check
        if action in ('USER_ADMIN', 'USER_AUTHOR', 'USER_VIEW', 'USER_MODIFY', 'USER_DELETE') and resource:
            # Check if USER_ADMIN permission in home project
            home_perm = PermissionCache(conf.home_env, username)
            if 'USER_ADMIN' in home_perm:
                return True

            userstore = conf.getUserStore()
            resource_user = userstore.getUserWhereId(resource.id)
            user = userstore.getUser(username)

            # Allow manage own and authored account
            if action in ('USER_ADMIN', 'USER_AUTHOR'):
                return resource_user.author_id == user.id or resource_user.id == user.id

            # Allow to manage itself
            return resource_user.id == user.id

        return True

