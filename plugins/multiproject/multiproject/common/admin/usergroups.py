# -*- coding: utf-8 -*-
"""
Provides admin permissions panel

URL /admin/permissions/groups
"""
import re

from genshi.core import Markup

from trac.env import open_environment
from trac.admin.api import IAdminPanelProvider
from trac.core import Component, implements
from trac.perm import PermissionCache
from trac.util.translation import _
from trac.util.html import plaintext
from trac.web.href import Href
from trac.web.chrome import add_notice, add_warning, add_script

from multiproject.common.projects import Projects
from multiproject.core.permissions import CQDEUserGroupStore, InvalidPermissionsState
from multiproject.core.permissions import CQDEOrganizationStore
from multiproject.core.configuration import conf
from multiproject.core.auth.auth import Authentication
from multiproject.common.membership.api import MembershipApi
from multiproject.common.notifications.email import EmailNotifier
from multiproject.common.environment import TracEnvironment


class UserGroupsAdminPanel(Component):
    implements(IAdminPanelProvider)

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        txt = 'Users'
        if conf.ldap_groups_enabled:
            txt = 'Users and LDAP'
        if 'PERMISSION_GRANT' in req.perm or 'PERMISSION_REVOKE' in req.perm:
            yield ('permissions', _('Permissions'), 'groups', _(txt))

    def render_admin_panel(self, req, cat, page, path_info):
        self.groupstore = CQDEUserGroupStore(self._get_environment_id())
        self.membership_requests = set()
        self.environment = TracEnvironment.read(conf.resolveProjectName(self.env))
        if self.environment.identifier != conf.sys_home_project_name:
            self.project = Projects().get_project(env_name = self.environment.identifier)
            self.memberships = MembershipApi(self.env, self.project)
            self.membership_requests = set(self.memberships.get_membership_requests())

        sorting = req.args.get('sorting')
        addmanyusers = False

        if req.method == 'POST':
            if 'save' in req.args:
                self.reorganize_users(req)
            if req.args.get('add'):
                self.add_user_to_group(req)
            elif req.args.get('add_organization'):
                self.add_organization_to_group(req)
            elif req.args.get('add_ldapgroup'):
                self.add_ldapgroup_to_group(req)
            elif req.args.get('remove'):
                if req.args.get('userremovelist'):
                    self.remove_user_from_group(req)
                if req.args.get('organizationremovelist'):
                    self.remove_organization_from_group(req)
                if req.args.get('ldapgroupremovelist'):
                    self.remove_ldapgroup_from_group(req)
            elif req.args.get('decline_membership'):
                self.decline_membership(req)
            elif req.args.get('sortbyuser'):
                sorting = 'user'
            elif req.args.get('sortbygroup'):
                sorting = 'group'
            elif req.args.get('add_users'):
                addmanyusers = True
            elif req.args.get('submit'):
                if not self.add_users_to_group(req):
                    addmanyusers = True

        # build template data

        user_groups = self.groupstore.get_all_user_groups()
        groups = self.groupstore.get_groups()
        all_groups = self.groupstore.get_groups()

        if conf.organizations_enabled:
            org_groups = self.groupstore.get_all_organization_groups()
            organizationstore = CQDEOrganizationStore.instance()
            organization_names = [org.name for org in organizationstore.get_organizations()]
        else:
            org_groups = []
            organization_names = []

        if conf.ldap_groups_enabled:
            ldapgroup_groups = self.groupstore.get_all_trac_environment_ldap_groups()
        else:
            ldapgroup_groups = []

        domain_name = conf.domain_name

        data = {
            'all_groups': all_groups,
            'user_groups': user_groups,
            'organization_groups': org_groups,
            'organizations': organization_names,
            'ldapgroup_groups': ldapgroup_groups,
            'sorting': sorting,
            'domain_name': domain_name,
            'groups': groups,
            'membership_requests': self.membership_requests,
            'ldap_groups_enabled': conf.ldap_groups_enabled,
            'organizations_enabled': conf.organizations_enabled
        }

        # Add jquery ui for drag'n'drop functionality
        add_script(req, 'multiproject/js/jquery-ui.js')

        if 'save' in req.args:
            return 'users_revoke_form.html', data
        if addmanyusers:
            return 'admin_addmanyusers.html', {'groups': groups}
        else:
            return 'admin_usergroups.html', data

    def reorganize_users(self, req):
        req.perm.require('PERMISSION_GRANT')
        req.perm.require('PERMISSION_REVOKE')

        data = self._read_groups_form(req)

        try:
            self.handle_users(req, data['u'])
            self.handle_organizations(req, data['o'])
            self.handle_ldap_groups(req, data['l'])
        except InvalidPermissionsState as e:
            req.send(e.value, content_type = 'text/html', status = 400)


    def _read_groups_form(self, req):
        # Read groups and their users
        users = {}
        organizations = {}
        ldap_groups = {}

        types = {'o':organizations, 'u':users, 'l':ldap_groups}

        for key in req.args.keys():
            if key.startswith('groups[') and key != 'groups[]':
                group = key[7:-3]
                for subject in self.__to_list(req.args[key]):
                    type = subject[0]
                    value = subject[2:]

                    # Select dict for org, ldap or user
                    target = types[type]

                    if not group in target:
                        target[group] = []
                    target[group] = target[group] + [value]
        return types

    def _init_states(self):
        """ Init empty mappings of all existing groups
        """
        current = {}
        next = {}
        all = self.groupstore.get_groups()
        for group in all:
            current[group] = set([])
            next[group] = set([])
        return all, current, next

    def handle_users(self, req, users_in_groups):
        all, current, next = self._init_states()

        # Check if end state is allowed
        ug = []
        for group, users in users_in_groups.items():
            ug += [(user, group) for user in users]
        self.groupstore.is_valid_group_members(user_groups = ug)

        # Build a mapping from the current state
        for user, group in self.groupstore.get_all_user_groups():
            current[group].add(user)

        # Build a mapping from the requested state
        for group, users in users_in_groups.items():
            next[group] |= set(users)

        # For each group, make necessary changes
        for group in all:
            add = next[group] - current[group]
            remove = current[group] - next[group]
            if add:
                for user in add:
                    self.groupstore.add_user_to_group(user, group)

            if remove:
                for user in remove:
                    self.groupstore.remove_user_from_group(user, group)

    def handle_organizations(self, req, orgs_in_groups):
        all, current, next = self._init_states()

        # Build mapping from the current state
        for org, group in self.groupstore.get_all_organization_groups():
            current[group].add(org)

        # Build mapping from requested state
        for group, organizations in orgs_in_groups.items():
            next[group] |= set(organizations)

        # For each group, make necessary changes
        for group in all:
            add = next[group] - current[group]
            remove = current[group] - next[group]

            if add:
                for organization in add:
                    self.groupstore.add_organization_to_group(organization, group)

            if remove:
                for organization in remove:
                    self.groupstore.remove_organization_from_group(organization, group)


    def handle_ldap_groups(self, req, ldaps_in_groups):
        all, current, next = self._init_states()

        # Build mapping from the current state
        for ldaps, group in self.groupstore.get_all_trac_environment_ldap_groups():
            current[group].add(ldaps)

        # Build mapping from requested state
        for group, ldaps in ldaps_in_groups.items():
            next[group] |= set(ldaps)

        # For each group, make necessary changes
        for group in all:
            add = next[group] - current[group]
            remove = current[group] - next[group]

            if add:
                for ldap_group in add:
                    self.groupstore.add_ldapgroup_to_group(ldap_group, group)

            if remove:
                for ldap_group in remove:
                    self.groupstore.remove_ldapgroup_from_group(ldap_group, group)


    def get_users(self, userlist):
        """
        Returns a list of valid users from the given string where
        each account is expected to presented on separate line

        :param str userlist: Users multiline string
        :return: List of users
        :rtype: list
        """
        users = []

        # Iterate lines
        for user in userlist.splitlines():
            user = plaintext(user, False).strip()
            if user:
                users.append(user)

        return users

    def add_users_to_group(self, req):
        """
        Add multiple users in a group

        :param Requests req:
            Request object containing following arguments:

            - users: String containing one or more users (one per each line)
            - group: Name of the group to add users to

        """
        req.perm.require('PERMISSION_GRANT')


        # Load home environment for checking the possibility to create local user
        home_env = open_environment(conf.getEnvironmentSysPath(conf.sys_home_project_name), use_cache=True)
        home_perm = PermissionCache(env=home_env, username=req.authname)
        create_link = Markup('<a href="%s">%s</a>' % (
            Href(conf.url_home_path)('admin/users/create_local', {'goto':req.abs_href(req.path_info)}),
            _('create a local user?'),
        ))

        auth = Authentication()
        users = self.get_users(req.args.get('users', '').strip())
        group = req.args.get('group', '').strip()

        if not users:
            add_warning(req, _("Users was left empty, please try again"))
            return
        if not group:
            add_warning(req, _("Group was left empty, please try again"))
            return

        notify_new_members = req.args.get('notify', None)

        accepted_members = set()
        succeeded = True
        for username in users:
            trac_username = self._get_trac_username(username)

            # User does not yet exists in multiproject database => retrieve and create user from authentication backend(s)
            if not trac_username:
                # Create user using authentication backends and sync functionality
                if not auth.sync_user(username):
                    # Show create local user option if in permissions
                    if 'USER_CREATE' in home_perm:
                        add_warning(req, _('User "%s" can not be found. Check name or ' % username) + create_link)
                    else:
                        add_warning(req, _('User "%s" can not be found. Please check the name' % username))
                    break

                add_notice(req, _('Added user %s to service' % username))
                # Now, retrieve the username again
                trac_username = auth.get_trac_username(username)

            pholders = {'who':trac_username, 'where':group}

            if not trac_username:
                add_warning(req, _('User %(who)s cannot be added to group %(where)s.', **pholders))
                succeeded = False
                continue

            if not self.groupstore.can_add_user_to_group(trac_username, group):
                add_warning(req, "Can't add anonymous to that group. Group contains permissions that are not allowed for anonymous.")
                return

            if self.groupstore.add_user_to_group(trac_username, group):
                add_notice(req, _('User %(who)s has been added to group %(where)s.', **pholders))
                accepted_members.add(trac_username)
            else:
                add_warning(req, _('User %(who)s cannot be added to group %(where)s.', **pholders))
                succeeded = False

        if self.environment.identifier != conf.sys_home_project_name:
            # Send a message to users. Those who requested membership will get a different mail than others.
            self.notify_accepted_memberships(req, self.membership_requests & accepted_members)
            if notify_new_members:
                self.notify_new_members(req, accepted_members - self.membership_requests)

        return succeeded

    def notify_accepted_memberships(self, req, members):
        for user in members:
            self.memberships.accept_membership(user)
            self.membership_requests = self.memberships.get_membership_requests()
            add_notice(req, _('Membership request has been accepted for %(who)s.', who = user))

    def notify_new_members(self, req, members):
        if len(members) > 0:
            users_store = conf.getUserStore()
            emails = users_store.get_emails(members)
            project = Projects().get_project(env_name = self.project.env_name)
            host = project.get_url()

            # TODO: Move to template
            if conf.site_name and len(conf.site_name) > 0:
                message = _("You have been invited to join the project %(p)s on %(s)s.\n\nYou can visit the project homepage at %(h)s\n\n"\
                            "Welcome to %(p)s on %(s)s", p = self.project.project_name, s = conf.site_name, h = str(host))
            else:
                message = _('You have been invited to join the project %(p)s on site.\n\nYou can visit the project homepage at %(h)s\n\nWelcome to %(p)s on site\n',
                            p = self.project.project_name, h = str(host))

            mailer = EmailNotifier(self.env, project, message)
            mailer.notify_emails("You have been invited", emails)

    def add_user_to_group(self, req):
        """
        Add single user to a group (both defined by request arguments)

        :param Request req:
            Request object, containing following arguments:

            - user: Name of the user to add in group
            - group: Name of the group where to add user

        .. NOTE:: If you want to add multiple users in a group at once, use :meth:`add_users_to_group`

        """
        req.perm.require('PERMISSION_GRANT')
        username = req.args.get('user', '').strip()
        groupname = req.args.get('group', '').strip()

        if not username:
            add_warning(req, _("User was left empty, please try again"))
            return
        if not groupname:
            add_warning(req, _("Group was left empty, please try again"))
            return

        # Get/check if user exists
        trac_username = self._get_trac_username(username)

        # User does not yet exists in multiproject database => retrieve and create user from authentication backend(s)
        if not trac_username:
            from multiproject.core.auth.auth import Authentication

            # Create user using authentication backends and sync functionality
            auth = Authentication()
            if not auth.sync_user(username):
                create_link = Markup('<a href="%s">%s</a>' % (
                                     Href(conf.url_home_path)('admin/users/create_local', {'goto':req.abs_href(req.path_info)}),
                                     _('create a local user?'),
                ))

                # Show warning with possibility to create a local user - if user has enough permissions.
                # Otherwise give traditional user cannot be found error
                home_perm = PermissionCache(env=conf.home_env, username=req.authname)

                if 'USER_CREATE' in home_perm:
                    add_warning(req, _('User "%s" can not be found. Check name or ' % username) + create_link)
                else:
                    add_warning(req, _('User "%s" can not be found. Please check the name' % username))

                return

            add_notice(req, _('Added user %s to service' % username))

            # Now, retrieve the username again
            trac_username = auth.get_trac_username(username)

        # If adding user in group it means that membership is accepted
        if trac_username in self.membership_requests:
            self.memberships.accept_membership(trac_username)
            self.membership_requests = self.memberships.get_membership_requests()
            add_notice(req, _('Membership request has been accepted for %(who)s.', who = trac_username))

        if not self.groupstore.can_add_user_to_group(trac_username, groupname):
            add_warning(req, "Can't add anonymous to that group. Group contains permissions that are not allowed for anonymous.")
            return

        if self.groupstore.add_user_to_group(trac_username, groupname):
            add_notice(req, _('User %(who)s has been added to group %(where)s.',
                                who = trac_username, where = groupname))
        else:
            add_warning(req, _('User %(who)s cannot be added to group %(where)s.',
                                who = trac_username, where = groupname))

    def add_organization_to_group(self, req):
        if not conf.organizations_enabled:
            return
        req.perm.require('PERMISSION_GRANT')
        organization = req.args.get('organization', '').strip()
        group = req.args.get('organizationgroup', '').strip()

        if not organization or not group:
            add_warning(req, 'You are trying to add a user type to a group, but you have not specified all the required parameters.')
            return

        if self.groupstore.add_organization_to_group(organization, group):
            add_notice(req, _('User type %(who)s has been added to group %(where)s.',
                                who = organization, where = group))
        else:
            add_warning(req, _('User type %(who)s cannot be added to group %(where)s.',
                                who = organization, where = group))

    def add_ldapgroup_to_group(self, req):
        if not conf.ldap_groups_enabled:
            return
        req.perm.require('PERMISSION_GRANT')
        ldapgroup = req.args.get('ldapgroup', '').strip()
        ldapgroup = ldapgroup.upper()
        group = req.args.get('usergroup', '').strip()

        if re.search(r'[^\_A-Z0-9]', ldapgroup): # allowed characters
            add_warning(req, 'LDAP group name can contain only alphanumeric characters and underline.')
            return

        if not ldapgroup or not group:
            add_warning(req, 'You are trying to add an LDAP group to a user group, but you have not specified all the required parameters.')
            return

        if self.groupstore.add_ldapgroup_to_group(ldapgroup, group):
            add_notice(req, _('LDAP group %(who)s has been added to group %(where)s.',
                                who = ldapgroup, where = group))
        else:
            add_warning(req, _('LDAP group %(who)s cannot be added to group %(where)s.',
                                 who = ldapgroup, where = group))

    def decline_membership(self, req):
        username = req.args.get('declineuser', '').strip()

        if not username:
            add_warning(req, _('Declined user cannot be found'))
            return

        self.memberships.decline_membership(username)
        self.membership_requests = self.memberships.get_membership_requests()
        add_notice(req, _('Membership request has been declined for %(who)s.', who = username))

    def remove_user_from_group(self, req):
        req.perm.require('PERMISSION_REVOKE')
        selection = req.args.get('userremovelist')
        selection = self.__to_list(selection)
        for item in selection:
            if item:
                user, group = item.split('::', 1)
                if self.groupstore.remove_user_from_group(user, group):
                    add_notice(req, _('User %(who)s has been removed from group %(where)s.',
                                        who = user, where = group))
                else:
                    add_warning(req, _('User %(who)s cannot be removed from group %(where)s.',
                                        who = user, where = group))

    def remove_organization_from_group(self, req):
        if not conf.organizations_enabled:
            return
        req.perm.require('PERMISSION_REVOKE')
        selection = req.args.get('organizationremovelist')
        selection = self.__to_list(selection)
        for item in selection:
            if item:
                organization, group = item.split('::', 1)
                if self.groupstore.remove_organization_from_group(organization, group):
                    add_notice(req, _('User type %(who)s has been removed from group %(where)s.',
                                        who = organization, where = group))
                else:
                    add_warning(req, _('User type %(who)s cannot be removed from group %(where)s.',
                                        who = organization, where = group))

    def remove_ldapgroup_from_group(self, req):
        if not conf.ldap_groups_enabled:
            return
        req.perm.require('PERMISSION_REVOKE')
        selection = req.args.get('ldapgroupremovelist')
        selection = self.__to_list(selection)
        for item in selection:
            if item:
                ldapgroup, group = item.split('::', 1)
                if self.groupstore.remove_ldapgroup_from_group(ldapgroup, group):
                    add_notice(req, _('LDAP group %(who)s has been removed from group %(where)s.',
                                        who = ldapgroup, where = group))
                else:
                    add_warning(req, _('LDAP group %(who)s cannot be removed from group %(where)s.',
                                        who = ldapgroup, where = group))

    def _get_environment_id(self):
        environment = TracEnvironment.read(conf.resolveProjectName(self.env))
        return environment.environment_id

    def _get_trac_username(self, username):
        a = Authentication()
        return a.get_trac_username(username)

    def __to_list(self, selection):
        return isinstance(selection, list) and selection or [selection]
