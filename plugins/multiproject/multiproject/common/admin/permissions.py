import re

from genshi.core import Markup
from trac.perm import PermissionSystem, PermissionCache
from trac.util.translation import _
from trac.admin.api import IAdminPanelProvider
from trac.core import Component, implements, TracError, ExtensionPoint
from trac.web.chrome import add_script, add_notice, add_stylesheet, add_warning, tag
from trac.web.href import Href

from multiproject.core.auth.auth import Authentication
from multiproject.core.restful import send_json
from multiproject.common.membership.api import MembershipApi
from multiproject.common.projects import Project
from multiproject.core.configuration import Configuration
from multiproject.core.permissions import CQDEUserGroupStore, CQDEOrganizationStore, InvalidPermissionsState

#
from multiproject.common.projects import Projects
from multiproject.common.projects.commands import MakeProjectPublic
from multiproject.common.projects.listeners import IProjectChangeListener
from multiproject.core.configuration import conf, DimensionOption
from multiproject.core.users import get_userstore


class PermissionsAdminPanel(Component):
    implements(IAdminPanelProvider)
    
    # Extension points
    project_change_listeners = ExtensionPoint(IProjectChangeListener)

    # list in order in which they should be listed in the UI
    MEMBER_TYPES = ('login_status', 'user', 'organization', 'ldap')

    def __init__(self):
        self.conf = Configuration.instance()

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if 'PERMISSION_GRANT' in req.perm or 'PERMISSION_REVOKE' in req.perm:
            yield ('general', _('General'), 'permissions', _('Permissions'))

    def render_admin_panel(self, req, cat, page, path_info):

        add_script(req, 'multiproject/js/jquery-ui.js')
        add_script(req, 'multiproject/js/permissions.js')
        add_stylesheet(req, 'multiproject/css/jquery-ui.css')
        add_stylesheet(req, 'multiproject/css/permissions.css')
        
        project = Project.get(self.env) #
        is_normal_project = self.env.project_identifier != \
                            self.env.config.get('multiproject', 'sys_home_project_name')

        # API instances
        perm_sys = PermissionSystem(self.env)
        group_store = CQDEUserGroupStore(env=self.env)
        org_store = CQDEOrganizationStore.instance()
        if is_normal_project:
            membership = MembershipApi(self.env, Project.get(self.env))
        else:
            membership = None

        if req.method == 'POST':
            action = req.args.get('action')
            if action == 'remove_member':
                self._remove_member(req, group_store)
            elif action == 'add_member':
                add_type = req.args.get('add_type')
                if add_type == 'user':
                    self._add_user(req, group_store, membership)
                elif add_type == 'organization':
                    self._add_organization(req, group_store)
                elif add_type == 'ldap_group':
                    self._add_ldap_group(req, group_store)
                elif add_type == 'login_status':
                    login_status = req.args.get('login_status')
                    if login_status not in ('authenticated', 'anonymous'):
                        raise TracError('Invalid arguments')
                    self._add_user(req, group_store, membership, username=login_status)
                else:
                    raise TracError('Invalid add_type')
            elif action == 'add_permission':
                self._add_perm_to_group(req, group_store, perm_sys)
            elif action == 'remove_permission':
                self._remove_permission(req, group_store, perm_sys)
            elif action == 'create_group':
                self._create_group(req, group_store, perm_sys)
            elif action == 'remove_group':
                self._remove_group(req, group_store)
            elif action == 'add_organization':
                self._add_organization(req, group_store)
            elif action == 'decline_membership':
                self._decline_membership(req, membership)
            elif 'makepublic' in req.args:
                project_api = Projects()
                if conf.allow_public_projects:
                    self._make_public(req, project)
                    project_api.add_public_project_visibility(project.id)
                    # Reload page
                    return req.redirect(req.href(req.path_info))
                else:
                    raise TracError("Public projects are disabled", "Error!")
            elif 'makeprivate' in req.args:
                project_api = Projects()
                self._make_private(req, project)
                project_api.remove_public_project_visibility(project.id)
                # Reload page
                return req.redirect(req.href(req.path_info))
            else:
                raise TracError('Unknown action %s' % action)

        # get membership request list after form posts have been processed
        if is_normal_project:
            membership_requests = set(membership.get_membership_requests())
        else:
            membership_requests = set()

        permissions = set(perm_sys.get_actions())

        # check if project if current configuration and permission state is in such state that
        # permission editions are likely fail
        invalid_state = None
        try:
            group_store.is_valid_group_members()
        except InvalidPermissionsState, e:
            add_warning(req, _('Application permission configuration conflicts with project permissions. '
                               'Before you can fully edit permissions or users you will need to either remove '
                               'offending permissions or set correct application configuration. Page reload'
                               'is required to update this warning.'))
            add_warning(req, e.message)

        return 'permissions.html', {
            'perm_data': self._perm_data(group_store, perm_sys),
            'theme_htdocs_location': self.env.config.get('multiproject', 'theme_htdocs_location', '/htdocs/theme'),
            'permissions': sorted(permissions),
            'organizations': sorted([org.name for org in org_store.get_organizations()]),
            'use_organizations': self.config.getbool('multiproject-users', 'use_organizations', False),
            'use_ldap': self.config.getbool('multiproject', 'ldap_groups_enabled', False),
            'membership_requests': membership_requests,
            'invalid_state': invalid_state,
            'is_public': project.public,
            'allow_public_projects': conf.allow_public_projects
        }

    def _perm_data(self, group_store, perm_sys):
        """
        Construct dict of groups, where each group is a dict which contains following keys::

            - members: list of tuples where first element is name and second type. eg. ('Marko', 'User')
            - permissions: list of permission names
            - implicit_count: number of permissions given implicitly trough higher permissions

        :param group_store: CQDEUserGroupStore
        :param perm_sys: Trac PermissionSystem
        :return: Dictionary containing the permission data for all groups
        """

        perm_data = {}

        # add all groups
        for group_name in group_store.get_groups():
            perm_data[group_name] = {}

        # add all members to groups
        for member, group_name in group_store.get_all_user_groups():
            group_dict = perm_data[group_name]
            member_type = 'user'
            if member in ('anonymous', 'authenticated'):
                member_type = 'login_status'
            group_dict.setdefault('members', []).append((member, member_type))

        # fill permission list
        explicit_perms = {}
        for group_name, permission in group_store.get_all_group_permissions():
            explicit_perms.setdefault(group_name, []).append(permission)
        for group_name, group_dict in perm_data.iteritems():
            group_dict = perm_data[group_name]
            for permission, enabled in perm_sys.get_user_permissions(group_name).iteritems():
                if not enabled:
                    continue
                permissions = group_dict.setdefault('permissions', [])
                entry = (permission, permission not in explicit_perms.get(group_name, []))
                permissions.append(entry)

        # fill organization list
        for organization_name, group_name in group_store.get_all_organization_groups():
            group_dict = perm_data[group_name]
            group_dict.setdefault('members', []).append((organization_name, 'organization'))

        # fill ldap group list
        for ldap_group_name, group_name in group_store.get_all_trac_environment_ldap_groups():
            group_dict = perm_data[group_name]
            group_dict.setdefault('members', []).append((ldap_group_name, 'ldap'))

        def member_cmp(a, b):
            type_order = self.MEMBER_TYPES
            if type_order.index(a[1]) == type_order.index(b[1]):
                return cmp(a[0], b[0])
            else:
                return cmp(type_order.index(a[1]), type_order.index(b[1]))

        # sort permissions and members
        for group_dict in perm_data.itervalues():
            group_dict['permissions'] = sorted(group_dict.get('permissions', []), key=lambda p: p[0])
            group_dict['members'] = sorted(group_dict.get('members', []), cmp=member_cmp)
            group_dict['implicit_count'] = len(filter(lambda p: p[1], group_dict.get('permissions', [])))

        return perm_data

    def _add_user(self, req, group_store, membership, username=None):
        """
        :param req: Request
        :param group_store: CQDEUserGroupStore
        :param membership: Membership API
        :param username: Override username from the request
        """
        req.perm.require('PERMISSION_GRANT')

        if username is None:
            username = req.args.get('member')
        group = req.args.get('group')

        if not username or not group:
            raise TracError('Invalid arguments while adding user')

        conf.log.exception("Member add - group_store: %s" % group_store)
        conf.log.exception("Member add - membership: %s" % membership)
        conf.log.exception("Member add - username: %s" % username)

        # Get/check if user exists
        auth = Authentication()
        username = auth.get_trac_username(username)

        # check if already exists
        if username in [e[0] for e in group_store.get_all_user_groups() if e[1] == group]:
            add_warning(req, _('User %(user)s already exists in the group %(group)s', group=group, user=username))
            return

        # User does not yet exists in multiproject database => retrieve and create user from authentication backend(s)
        if not username:
            username = req.args.get('member')
            # Create user using authentication backends and sync functionality
            if not auth.sync_user(username):
                # Show warning with possibility to create a local user - if user has enough permissions.
                # Otherwise give traditional user cannot be found error
                home_perm = PermissionCache(env=self.conf.home_env, username=req.authname)

                if 'USER_CREATE' in home_perm:
                    link = Href(self.conf.url_home_path)('admin/users/create_local',
                                                         {'goto': req.abs_href(req.path_info)})
                    create_link = Markup('<a href="%s">%s</a>' % (link, _('create a local user?')))
                    add_warning(req, _('User "%(username)s" can not be found. Check name or ',
                                username=username) + create_link)
                else:
                    add_warning(req, _('User "%(username)s" can not be found. Please check the name.',
                                username=username))
                return

            add_notice(req, _('Added user %s to service' % username))
            # Now, retrieve the username again
            username = auth.get_trac_username(username)

        # when adding to normal project, accept possible membership requests
        if membership is not None:
            # If adding user in group it means that membership is accepted
            if username in membership.get_membership_requests():
                membership.accept_membership(username)
                add_notice(req, _('Membership request has been accepted for %(who)s.', who=username))

        try:
            group_store.add_user_to_group(username, group)
            add_notice(req, _('User %(who)s has been added to group %(where)s.',
                       who=username, where=group))
        except InvalidPermissionsState, e:
            add_warning(req, _('User %(who)s cannot be added to group %(where)s. %(reason)s',
                        who=username, where=group, reason=e.message))

    def _add_perm_to_group(self, req, group_store, perm_sys):
        req.perm.require('PERMISSION_GRANT')

        group = req.args.get('group')
        permission = req.args.get('permission')

        if not permission:
            add_warning(req, _('No permission selected, please select permission to add.'))
            return

        if permission not in perm_sys.get_actions():
            raise TracError('Invalid permission')

        if group is None or permission is None:
            raise TracError('Invalid arguments')

        # disallow explicitly giving same permission again
        for group_name, explicit_perm in group_store.get_all_group_permissions():
            if group != group_name:
                continue
            if permission == explicit_perm:
                add_warning(req, _("Permission %(permission)s already exists in %(group)s.",
                    permission=permission, group=group))
                return

        # TODO: this was in original ui implementation, but why?
        req.perm.require(permission)

        try:
            group_store.grant_permission_to_group(group, permission)
            add_notice(req, _('The group %(where)s has been granted the permission %(what)s.',
                       where=group, what=permission))
        except InvalidPermissionsState, e:
            add_warning(req, _('The permission %(what)s cannot be granted to group %(where)s. %(reason)s',
                        what=permission, where=group, reason=e.message))

    def _remove_group(self, req, group_store):
        req.perm.require('PERMISSION_REVOKE')

        group = req.args.get('group')
        if group is None:
            raise TracError('Invalid arguments')

        if group_store.remove_group(group):
            add_notice(req, _('The group %(what)s has been removed.', what=group))
        else:
            add_warning(req, _('The group %(what)s cannot be removed.', what=group))

    def _remove_member(self, req, group_store):
        req.perm.require('PERMISSION_REVOKE')

        member = req.args.get('member')
        member_type = req.args.get('type')
        group = req.args.get('group')

        if not member or not group or member_type not in self.MEMBER_TYPES:
            raise TracError('Invalid arguments')

        if member_type in ('user', 'login_status'):
            try:
                group_store.remove_user_from_group(member, group)
                send_json(req, {})
            except InvalidPermissionsState, e:
                req.send(e.message, content_type='text/plain', status=403)
            except ValueError, e:
                req.send(e.message, content_type='text/plain', status=403)

        elif member_type == 'organization':
            group_store.remove_organization_from_group(member, group)
            req.send('SUCCESS', content_type='text/html', status=200)

        elif member_type == 'ldap':
            group_store.remove_ldapgroup_from_group(member, group)
            req.send('SUCCESS', content_type='text/html', status=200)

    def _remove_permission(self, req, group_store, perm_sys):
        req.perm.require('PERMISSION_REVOKE')

        group = req.args['group']
        permission = req.args['permission']

        def group_perms():
            res = []
            for permission, enabled in perm_sys.get_user_permissions(group).iteritems():
                if not enabled:
                    continue
                res.append(permission)
            return res

        try:
            before = group_perms()
            group_store.revoke_permission_from_group(group, permission)
            removed = set(before) - set(group_perms())
            remaining = self._perm_data(group_store, perm_sys)[group]['implicit_count']
            send_json(req, {'result': 'SUCCESS',
                            'removed': list(removed),
                            'remaining': remaining})
        except InvalidPermissionsState, e:
            req.send(e.message, content_type='text/plain', status=403)

    def _create_group(self, req, group_store, perm_sys):
        req.perm.require('PERMISSION_GRANT')

        group_perms = req.args.get('group_perms')
        group_name = req.args.get('group_name')

        # if only one permission selected
        if isinstance(group_perms, basestring):
            group_perms = [group_perms]

        if not group_name:
            add_warning(req, _('Invalid group name'))
            return

        # trac schema limitation
        if group_name.isupper():
            add_warning(req, _('Group name cannot be in all upper cases'))
            return

        valid_perms = perm_sys.get_actions()
        for perm in group_perms:
            if perm not in valid_perms:
                raise TracError('Invalid permission %s' % perm)
            try:
                group_store.grant_permission_to_group(group_name, perm)
            except InvalidPermissionsState, e:
                add_warning(req, _('Unable to add permission %(perm)s to group %(group)s. %(reason)s',
                            perm=perm, group=group_name, reason=e.message))

    def _add_organization(self, req, group_store):
        req.perm.require('PERMISSION_GRANT')

        group_name = req.args.get('group')
        organization = req.args.get('organization')

        try:
            group_store.add_organization_to_group(organization, group_name)
            add_notice(req, _('Organization %(organization)s added to group %(group)s',
                       group=group_name, organization=organization))
        except ValueError:
            add_warning(req, _('Organization %(organization)s already exists in group %(group)s',
                        group=group_name, organization=organization))

    def _add_ldap_group(self, req, group_store):
        req.perm.require('PERMISSION_GRANT')

        group_name = req.args.get('group')
        ldap_group_name = req.args.get('ldap_group', '').strip()
        ldap_group_name = ldap_group_name.upper()

        if re.search(r'[^\_A-Z0-9]', ldap_group_name):  # allowed characters
            add_warning(req, 'LDAP group name can contain only alphanumeric characters and underline.')
            return

        if not ldap_group_name:
            add_warning(req, _('You are trying to add an LDAP group to a user group, '
                               'but you have not specified all the required parameters.'))
            return

        group_store.add_ldapgroup_to_group(ldap_group_name, group_name)
        add_notice(req, _('LDAP group %(who)s has been added to group %(where)s.',
                   who=ldap_group_name, where=group_name))

    def _decline_membership(self, req, membership):
        username = req.args.get('applicant')

        if not username:
            add_warning(req, _('Declined user cannot be found'))
            return

        membership.decline_membership(username)
        add_notice(req, _('Membership request has been declined for %(who)s.', who=username))

    def _make_public(self, req, project):
        cmd = MakeProjectPublic(project)
        if cmd.do():
            # Notify listeners
            for listener in self.project_change_listeners:
                listener.project_set_public(project)
            # Notify user
            add_notice(req, tag(
                _("Project published: "), _('public groups added')
            ))
        else:
            add_warning(req, "Failed to publish project")

    def _make_private(self, req, project):
        cmd = MakeProjectPublic(project)
        if cmd.undo():
            # Notify listeners
            for listener in self.project_change_listeners:
                listener.project_set_private(project)
            # Notify user
            add_notice(req, tag(
                _("Unpublished project: "), _('public groups removed')
            ))
        else:
            add_warning(req, "Failed to unpublish project")
