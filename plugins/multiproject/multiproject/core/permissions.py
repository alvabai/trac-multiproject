# -*- coding: utf-8 -*-
from multiproject.core.configuration import conf
from multiproject.core.cache.permission_cache import GroupPermissionCache
from multiproject.core.exceptions import SingletonExistsException
from multiproject.core.db import admin_query, admin_transaction, safe_int


class InvalidPermissionsState(Exception):
    pass


class CQDEPermissionStore(object):
    """
    Provides methods that are required by Trac IPermissionStore

    .. NOTE:: Avoid using directly. Instead use Trac ``PermissionSystem``.

    """

    def __init__(self, trac_environment_key):
        self._store = CQDEUserGroupStore(trac_environment_key)

    def get_user_permissions(self, subject):
        """
        Returns the permissions of the specific subject (user or group)

        .. NOTE::

            Argument ``subject`` can be group or user, even though method name
            would indicate only user being correct. This is how Trac
            implements groups (at least in 0.12)

        .. WARNING:: Group name as ``subject`` not supported yet.

        :returns: List of permission names
        """
        user_store = conf.getUserStore()
        user = user_store.getUser(subject)

        user_groups = self._store.get_all_user_groups()
        group_perms = self._store.get_all_group_permissions()
        organization_groups = self._store.get_all_organization_groups()

        groups = []
        for username, group in user_groups:
            if username == user.username:
                groups.append(group)

        org_store = CQDEOrganizationStore.instance()
        for org, group in organization_groups:
            org_id = org_store.get_organization_id(org)
            if org_id in user.organization_keys:
                groups.append(group)

        permissions = []
        for group, perm in group_perms:
            if group in groups:
                permissions.append(perm)

        return permissions

    def get_users_with_permissions(self, permission_names):
        """
        Gives only users that have direct permission through group
        Will not give users through organizations (in some cases list would be long)

        .. NOTE::

            This method is needed only by ticket system to
            restrict ticket owner or list possible owners.
            Keep ``restrict_owner = false`` on trac.ini.
        """
        user_groups = self._store.get_all_user_groups()
        group_perms = self._store.get_all_group_permissions()

        groups = []
        for group, perm in group_perms:
            if perm in permission_names:
                groups.append(group)

        users = []
        for user, group in user_groups:
            if group in groups:
                users.append(user)
        return users

    def get_all_permissions(self):
        """ Returns (group, permission) pairs
        """
        return self._store.get_all_group_permissions()

    def grant_permission(self, username, permission):
        raise Exception("You can't grant/revoke permission for user directly. Use groups instead.")

    def revoke_permission(self, username, permission):
        raise Exception("You can't grant/revoke permission for user directly. Use groups instead.")

    # TODO: only used in discussion, refactor out!
    def get_user_project_groups(self, audit_username):
        user_store = conf.getUserStore()
        user = user_store.getUser(audit_username)

        user_groups = self._store.get_all_user_groups()

        groups = []
        for username, group in user_groups:
            if username == user.username:
                groups.append(group)

        return groups


class CQDEUserGroupStore(object):
    """ DAO for user groups
    """

    def __init__(self, trac_environment_key):
        self._cache = GroupPermissionCache.instance()
        self._helper = CQDEPermissionHelper.instance()
        self._organizations = CQDEOrganizationStore.instance()
        self._ldapgroups = CQDELdapGroupStore.instance()
        self.trac_environment_key = trac_environment_key

    def is_public_project(self):
        """
        Function checks if the project defined in ``self.trac_environment_key``
        is considered public. This is True if anonymous user group has permissions
        defined in configuration. Example::

          public_anon_group = Public viewers:VIEW,VERSION_CONTROL_VIEW

        Otherwise the project is private and function will return False.
        """
        # Read the public group permissions from config (key returns tuple: (groupname, list of permissions))
        required_group_perms = conf.public_anon_group[1]

        permissions = []
        with admin_query() as cursor:
            cursor.callproc("get_project_public_permissions", [self.trac_environment_key])
            permissions = cursor.fetchall()

        public_group_perms = [pgp[0] for pgp in permissions]

        # Iterate required permission and ensure all of the are found. Generated list contains the missing
        # permissions and thus the outcome is: True=public, False=private
        missing_perms = [rgp for rgp in required_group_perms if rgp not in public_group_perms]

        # All the required 'public project' permissions were found => Public project
        return len(missing_perms) == 0

    def get_groups(self):
        """ Returns a list of group names in the trac environment
        """
        groups = []
        with admin_query() as cursor:
            try:
                cursor.callproc("get_groups", [self.trac_environment_key])
                for row in cursor:
                    groups.append(row[0])
            except:
                conf.log.exception("Exception. get_groups(%s) procedure failed." % str(self.trac_environment_key))

        return groups

    def can_remove_group(self, group_name):
        """ Checks that group can be removed and trac environment
            will still have an admin user
        """
        # If you can revoke trac_admin from group it must be ok
        return self.can_revoke_trac_admin(group_name)

    def can_revoke_trac_admin(self, group_name):
        """ Checks that it is ok to remove TRAC_ADMIN permission from group
        """
        gp = self.get_all_group_permissions()
        gp = [(group, perm) for group, perm in gp if not (group == group_name and perm == 'TRAC_ADMIN')]
        try:
            self.is_valid_group_members(group_permissions=gp)
            return True
        except InvalidPermissionsState:
            return False

    def can_remove_user_from_group(self, group_name, username):
        """ Checks that it is ok to remove user from group
        """
        ug = self.get_all_user_groups()
        ug = [(user, group) for user, group in ug if not (user == username and group == group_name)]
        try:
            self.is_valid_group_members(user_groups=ug)
            return True
        except InvalidPermissionsState:
            return False

    def can_add_user_to_group(self, username, group_name):
        """ Anonymous can not be added in the group which contains
            too much permissions
        """
        ug = self.get_all_user_groups() + [(username, group_name)]
        try:
            self.is_valid_group_members(user_groups=ug)
            return True
        except InvalidPermissionsState:
            return False

    def can_grant_permission_to_group(self, group_name, permission_name):
        """ If anonymous is in a group, there are limitations of
            what permissions can be added
        """
        gp = self.get_all_group_permissions() + [(group_name, permission_name)]
        try:
            self.is_valid_group_members(group_permissions=gp)
            return True
        except InvalidPermissionsState:
            return False

    def is_valid_group_members(self, group_permissions=None, user_groups=None):
        """
        Check whether the requested users and groups state is allowed or not

        Group members state is given in parameters. Any parameter can be left
        out and then the current state is used for that parameter.

        :param list group_permissions: List of tuples (group, privilege)
        :param list user_groups: List of tuples (username, groupname)
        :raises: InvalidPermissionsState with user friendly error message in a case of error
        """
        group_permissions = group_permissions or self.get_all_group_permissions()
        user_groups = user_groups or self.get_all_user_groups()

        # Prepare group-privilege and privilege-group mappings
        gp, pg = self._group_tuples(group_permissions)
        # Prepare user-group and group-user mappings
        ug, gu = self._group_tuples(user_groups)

        # 1. Check that anonymous does not get too heavy privileges
        # Anonymous can not be part of any organization or ldap so it's enough to check ug.
        anon_forbidden = set(conf.anon_forbidden_actions)
        if 'anonymous' in ug:
            for group in ug['anonymous']:
                privileges = anon_forbidden & gp[group]
                if privileges:
                    items = tuple(privileges)
                    is_are = "are"
                    if len(items) == 1:
                        is_are = "is"
                        items = items[0]

                    raise InvalidPermissionsState(
                        "%s %s not allowed for anonymous. Anonymous would get this from %s." % (
                        str(items), is_are, group))

        # 2. Check that there's always someone having TRAC_ADMIN privilege
        users_with_admin = set([])
        if 'TRAC_ADMIN' not in pg:
            raise InvalidPermissionsState("Trac needs an administrator (someone with TRAC_ADMIN privilege)")
        for group in pg['TRAC_ADMIN']:
            if group in gu:
                users_with_admin |= gu[group]
        if not users_with_admin:
            raise InvalidPermissionsState("Trac needs an administrator (someone with TRAC_ADMIN privilege)")

    def _group_tuples(self, tuples):
        """ Groups tuples by items in both ways
            Works only with two item tuples
        """
        ab = {}
        ba = {}
        for a, b in tuples:
            if a not in ab:
                ab[a] = set([])
            if b not in ba:
                ba[b] = set([])
            ba[b].add(a)
            ab[a].add(b)
        return ab, ba

    def get_all_user_groups(self):
        """
        :returns: List of tuples (username, group)
        """
        envkey = self.trac_environment_key
        user_groups = self._cache.get_user_groups(envkey)
        if user_groups is not None:
            return user_groups

        user_groups = []

        with admin_query() as cursor:
            try:
                cursor.callproc("get_all_user_groups", [envkey])
                for row in cursor:
                    # Tuple: (username, groupname)
                    user_groups.append((row[0], row[1]))
                self._cache.set_user_groups(envkey, user_groups)
            except:
                conf.log.exception("Exception. get_all_user_groups(%s) procedure failed." % str(envkey))

        return user_groups

    def get_user_count_from_groups(self):
        users = {}
        organizations = {}
        user_groups = self.get_all_user_groups()
        for username, groupname in user_groups: #@UnusedVariable
            if groupname in users:
                users[groupname] += 1
            else:
                users[groupname] = 1
        org_groups = self.get_all_organization_groups()
        for organization, groupname in org_groups: #@UnusedVariable
            if groupname in organizations:
                organizations[groupname] += 1
            else:
                organizations[groupname] = 1
        return [users, organizations]

    def get_all_organization_groups(self):
        """
        :returns: a list of tuples (organization_name, group_name)
        """
        org_groups = self._cache.get_organization_groups(self.trac_environment_key)
        if org_groups is not None:
            return org_groups

        org_groups = []

        with admin_query() as cursor:
            try:
                cursor.callproc("get_all_organization_groups", [self.trac_environment_key])
                for row in cursor:
                    org_groups.append((row[0], row[1]))
                self._cache.set_organization_groups(self.trac_environment_key, org_groups)
            except:
                conf.log.exception(
                    "Exception. get_all_organization_groups(%s) procedure failed." % str(self.trac_environment_key))

        return org_groups

    def get_all_group_permissions(self):
        """
        :returns: a list of groups and their permissions
        """
        group_perms = self._cache.get_group_perms(self.trac_environment_key)
        if group_perms is not None:
            return group_perms

        group_perms = []
        with admin_query() as cursor:
            try:
                cursor.callproc("get_all_group_permissions", [self.trac_environment_key])
                for row in cursor:
                    group_perms.append((row[0], row[1]))
                self._cache.set_group_perms(self.trac_environment_key, group_perms)
            except:
                conf.log.exception(
                    "Exception. get_all_group_permissions(%s) procedure failed." % str(self.trac_environment_key))

        return group_perms

    def create_group(self, group_name):
        # Clear trac environment group cache
        self._cache.clear_user_groups(self.trac_environment_key)
        self._cache.clear_organization_groups(self.trac_environment_key)
        self._cache.clear_group_perms(self.trac_environment_key)

        group_name = group_name.encode('utf-8')
        return self._helper.call_proc_with_success("create_group",
            [group_name, self.trac_environment_key])

    def remove_group(self, group_name):
        """
        Removes group.
        Updates the published time of the project accordingly.
        """
        if not self.can_remove_group(group_name):
            return False

        group_name = group_name.encode('utf-8')
        group_id = self.get_group_id(group_name)

        # Clear trac environment group cache
        self._cache.clear_user_groups(self.trac_environment_key)
        self._cache.clear_organization_groups(self.trac_environment_key)
        self._cache.clear_group_perms(self.trac_environment_key)
        self._cache.clear_group_id(group_name, self.trac_environment_key)

        result = self._helper.call_proc_with_success("remove_group",
            [group_id])

        self._update_published_time()
        return result

    def add_user_to_group(self, username, group_name):
        """
        Adds user to group.
        Updates the published time of the project accordingly.
        """
        userstore = conf.getUserStore()
        user = userstore.getUser(username)

        if not user:
            from multiproject.core.auth.auth import Authentication

            auth = Authentication()
            auth.sync_user(username)
            user = userstore.getUser(username)

        if not user:
            return False

        # Create group if it doesn't exist
        group_name = group_name.encode('utf-8')
        group_id = self.get_group_id(group_name)
        if group_id is None:
            self.create_group(group_name)
            group_id = self.get_group_id(group_name)

        self._cache.clear_user_groups(self.trac_environment_key)

        result = self._helper.call_proc_with_success("add_user_to_group",
            [user.id, group_id])

        self._update_published_time()
        return result

    def remove_user_from_group(self, username, group_name):
        """
        Removes user from group.
        Updates the published time of the project accordingly.
        """
        if not self.can_remove_user_from_group(group_name, username):
            return False

        userstore = conf.getUserStore()
        user = userstore.getUser(username)
        if not user:
            return False

        group_name = group_name.encode('utf-8')
        group_id = self.get_group_id(group_name)
        self._cache.clear_user_groups(self.trac_environment_key)

        result = self._helper.call_proc_with_success("remove_user_from_group",
            [user.id, group_id])

        self._update_published_time()
        return result

    def add_organization_to_group(self, organization_name, group_name):
        organization_id = self._organizations.get_organization_id(organization_name)

        # Create group if it doesn't exist
        group_name = group_name.encode('utf-8')
        group_id = self.get_group_id(group_name)
        if group_id is None:
            self.create_group(group_name)
            group_id = self.get_group_id(group_name)

        self._cache.clear_organization_groups(self.trac_environment_key)

        return self._helper.call_proc_with_success("add_organization_to_group",
            [organization_id, group_id])

    def remove_organization_from_group(self, organization_name, group_name):
        organization_id = self._organizations.get_organization_id(organization_name)
        group_name = group_name.encode('utf-8')
        group_id = self.get_group_id(group_name)

        self._cache.clear_organization_groups(self.trac_environment_key)

        return self._helper.call_proc_with_success("remove_organization_from_group",
            [organization_id, group_id])

    def grant_permission_to_group(self, group_name, permission_name):
        """
        Grants permission to group.
        Updates the published time of the project accordingly.
        """
        permission_id = self._helper.get_permission_id(permission_name)

        # Create group if it doesn't exist
        group_name = group_name.encode('utf-8')
        group_id = self.get_group_id(group_name)
        if group_id is None:
            self.create_group(group_name)
            group_id = self.get_group_id(group_name)

        self._cache.clear_group_perms(self.trac_environment_key)

        result = self._helper.call_proc_with_success("grant_permission_to_group",
            [group_id, permission_id])

        self._update_published_time()

        return result

    def revoke_permission_from_group(self, group_name, permission_name):
        """
        Revokes permission to group.
        Updates the published time of the project accordingly.
        """
        if permission_name == 'TRAC_ADMIN':
            if not self.can_revoke_trac_admin(group_name):
                return False

        permission_id = self._helper.get_permission_id(permission_name)
        group_name = group_name.encode('utf-8')
        group_id = self.get_group_id(group_name)

        self._cache.clear_group_perms(self.trac_environment_key)

        result = self._helper.call_proc_with_success("revoke_permission_from_group",
            [group_id, permission_id])

        self._update_published_time()

        return result

    def get_group_id(self, group_name):
        # Try from cache
        gid = self._cache.get_group_id(group_name, self.trac_environment_key)
        if gid is not None:
            return gid

        with admin_query() as cursor:
            try:
                cursor.callproc("get_group_id", [group_name, self.trac_environment_key])
                row = cursor.fetchone()
                if row:
                    gid = row[0]
                    self._cache.set_group_id(group_name, self.trac_environment_key, gid)
            except:
                params = (str(group_name), str(self.trac_environment_key))
                conf.log.exception("Exception. get_group_id(%s, %s) procedure failed." % params)

        return gid

    def add_ldapgroup_to_group(self, ldapgroup_name, group_name):
        # Create ldap group if it doesn't exist
        ldapgroup_name = ldapgroup_name.encode('utf-8')
        ldapgroup_id = self._ldapgroups.get_ldapgroup_id(ldapgroup_name)
        if ldapgroup_id is None:
            if not self._ldapgroups.store_ldapgroup(ldapgroup_name):
                conf.log.error("LDAP: Storing new ldap group %s failed. (user group %s)" %
                               (ldapgroup_name, group_name))
            ldapgroup_id = self._ldapgroups.get_ldapgroup_id(ldapgroup_name)

        # Create group if it doesn't exist
        group_name = group_name.encode('utf-8')
        group_id = self.get_group_id(group_name)
        if group_id is None:
            self.create_group(group_name)
            group_id = self.get_group_id(group_name)

        self._cache.clear_trac_environment_ldap_groups(self.trac_environment_key)

        result = self._helper.call_proc_with_success("add_ldapgroup_to_group",
            [ldapgroup_id, group_id])
        if not result:
            conf.log.error("LDAP: Adding LDAP group %s to group %s failed. (ldap group %s, group %s)" %
                           (ldapgroup_id, group_id, ldapgroup_name, group_name))

        return result

    def remove_ldapgroup_from_group(self, ldapgroup_name, group_name):
        ldapgroup_id = self._ldapgroups.get_ldapgroup_id(ldapgroup_name)
        group_name = group_name.encode('utf-8')
        group_id = self.get_group_id(group_name)

        self._cache.clear_trac_environment_ldap_groups(self.trac_environment_key)

        return self._helper.call_proc_with_success("remove_ldapgroup_from_group",
            [ldapgroup_id, group_id])

    def get_all_trac_environment_ldap_groups(self):
        """ Returns list of tuples (ldapgroup, group)
        """
        ldapgroups = self._cache.get_trac_environment_ldap_groups(self.trac_environment_key)
        if ldapgroups is not None:
            return ldapgroups

        ldapgroups = []
        with admin_query() as cursor:
            try:
                cursor.callproc("get_all_ldap_groups_by_trac_environment_key", [self.trac_environment_key])
                for row in cursor:
                    ldapgroups.append((row[0], row[1]))
                self._cache.set_trac_environment_ldap_groups(self.trac_environment_key, ldapgroups)
            except:
                conf.log.exception("Exception. get_all_ldap_groups_by_trac_environment_key(%s) procedure failed." %
                                   str(self.trac_environment_key))

        return ldapgroups

    def _update_published_time(self):
        """
        Updates NULL published date, if needed.
        Sets it to NULL, if project is not published,
        and to current timestamp, if it is published and published was NULL.
        """
        # TODO: remove circular references from Project class and move this method to there

        if not self.is_public_project():
            query = "UPDATE projects SET `published` = NULL WHERE trac_environment_key = %s"
        else:
            query = ("UPDATE projects SET `published` = now() "
                    "WHERE trac_environment_key = %s AND published IS NULL")

        with admin_transaction() as cursor:
            try:
                cursor.execute(query, self.trac_environment_key)
            except Exception as e:
                conf.log.exception("Exception. Failed updating project publish data with query '''%s'''" % query)
                raise


class CQDESuperUserStore(object):
    _instance = None

    def __init__(self):
        if CQDESuperUserStore._instance:
            raise SingletonExistsException("Use CQDESuperUserStore.instance()")
        self._cache = GroupPermissionCache.instance()
        self._helper = CQDEPermissionHelper.instance()

    @staticmethod
    def instance():
        if CQDESuperUserStore._instance is None:
            CQDESuperUserStore._instance = CQDESuperUserStore()
        return CQDESuperUserStore._instance

    def get_superusers(self):
        """ Return list of usernames of superusers
        """
        superusers = self._cache.get_superusers()
        if superusers is not None:
            return superusers

        superusers = []

        with admin_query() as cursor:
            try:
                cursor.callproc("get_superusers")
                for row in cursor:
                    superusers.append((row[0]))
                self._cache.set_superusers(superusers)
            except:
                conf.log.exception("Exception. get_superusers procedure call failed")

        return superusers

    def add_superuser(self, username):
        """ Add user to superusers list
        """
        userstore = conf.getUserStore()
        if not userstore.userExists(username):
            return False

        if self._helper.call_proc_with_success("add_superuser", [username]):
            self._cache.clear_superusers()
            return True
        return False

    def remove_superuser(self, username):
        """ Add user to superusers list
        """
        userstore = conf.getUserStore()
        if not userstore.userExists(username):
            return False

        if self._helper.call_proc_with_success("remove_superuser", [username]):
            self._cache.clear_superusers()
            return True
        return False

    def is_superuser(self, username):
        if username in self.get_superusers():
            return True
        return False


class CQDEPermissionHelper(object):
    """ Provides helper methods that are needed on permission classes
    """
    _instance = None

    def __init__(self):
        if CQDEPermissionHelper._instance:
            raise SingletonExistsException("Use CQDEPermissionHelper.instance()")
        self._cache = GroupPermissionCache.instance()

    @staticmethod
    def instance():
        if CQDEPermissionHelper._instance is None:
            CQDEPermissionHelper._instance = CQDEPermissionHelper()
        return CQDEPermissionHelper._instance

    def get_permission_id(self, permission_name):
        """ Get permission key from cache or db
        """
        permission_id = self._cache.get_permission_id(permission_name)
        if permission_id is not None:
            return permission_id

        with admin_query() as cursor:
            try:
                cursor.execute("SELECT action_id FROM action WHERE action_string = %s", permission_name)
                row = cursor.fetchone()
                if row is not None:
                    permission_id = row[0]
                    self._cache.set_permission_id(permission_name, permission_id)
            except:
                conf.log.exception("Exception. Failed getting permission id for '%s'" % str(permission_name))

        if not permission_id:
            permission_id = self.create_permission_id(permission_name)

        return permission_id

    def create_permission_id(self, permission_name):
        """ Create permission and return its id
        """
        permission_id = None

        with admin_transaction() as cursor:
            try:
                cursor.execute("INSERT INTO action(action_string) VALUES(%s)", permission_name)
                cursor.execute("SELECT action_id FROM action WHERE action_string = %s", permission_name)
                row = cursor.fetchone()
                if row is not None:
                    permission_id = row[0]
                    self._cache.set_permission_id(permission_name, permission_id)
            except:
                conf.log.exception("Exception. Failed creating permission id with name '%s'" % str(permission_name))
                raise

        return permission_id

    def call_proc_with_success(self, name, args):
        """ Helper method for wrapping database connection initialization
            and Exception handling away from code that wont need it.

            To be used with queries that can throw away it's results
            and should just succesfully run.

            Returns true/false to tell if query failed or not

        """
        try:
            with admin_query() as cursor:
                cursor.callproc(name, args)
        except:
            return False

        return True

    def parse_enum_type(self, enum_str):
        methods = []
        enum_str = enum_str.replace('enum(', '').strip(')')
        for item in enum_str.split(','):
            methods.append(item.strip("' "))

        return methods


class CQDEAuthenticationStore(object):
    """ DAO for authentications
    """
    _instance = None

    def __init__(self):
        if CQDEAuthenticationStore._instance:
            raise SingletonExistsException("Use CQDEAuthenticationStore.instance()")
        self.__helper = CQDEPermissionHelper.instance()
        self.__cache = GroupPermissionCache.instance()

        # Consider for not hardcoding this
        self.LOCAL = 'LocalDB'
        # self.LDAP also hardcoded in ldap_auth.py
        self.LDAP = 'LDAP'

    @staticmethod
    def instance():
        if CQDEAuthenticationStore._instance is None:
            CQDEAuthenticationStore._instance = CQDEAuthenticationStore()
        return CQDEAuthenticationStore._instance

    def _compare(self, id, name):
        return id == self.get_authentication_id(name)

    def is_local(self, id):
        return self._compare(id, self.LOCAL)

    def is_ldap(self, id):
        return self._compare(id, self.LDAP)

    def is_authenticated_by(self, id, name):
        """
        Check if user is authenticated with method ``name``
        :param string name: Authentication name
        :return: True or False
        :raises: ValueError if ``name`` is not known authentication method
        """
        if not name in [auth.name for auth in self.get_authentications()]:
            raise ValueError('%s is not known authentication method in the database' % name)
        return self._compare(id, name)

    def get_authentications(self):
        """ Returns a list of AuthenticationEntity class instances
        """
        authentications = []
        with admin_query() as cursor:
            try:
                cursor.execute("SELECT * FROM authentication")

                for row in cursor:
                    auth = AuthenticationEntity()
                    auth.id = row[0]
                    auth.name = row[1]
                    authentications.append(auth)
            except:
                conf.log.exception("Exception. Failed to get authentications.")

        return authentications

    def get_authentication_method(self, authentication_id):
        """ Returns authentication method
        """
        method = None

        # For anonymous users, this is None
        if authentication_id is None:
            return None

        with admin_query() as cursor:
            try:
                cursor.execute(
                    "SELECT method FROM authentication WHERE id = %d " % safe_int(authentication_id))
                row = cursor.fetchone()
                if row:
                    method = row[0]
            except:
                conf.log.exception("Exception. get_authentication_method failed.")
                raise

        return method

    def get_authentication_id(self, authentication_name):
        authentication_id = self.__cache.get_authentication_id(authentication_name)
        if authentication_id is not None:
            return authentication_id

        with admin_query() as cursor:
            try:
                query = "SELECT id FROM authentication WHERE authentication.method = %s"
                cursor.execute(query, authentication_name)
                row = cursor.fetchone()
                if row:
                    authentication_id = row[0]
                    self.__cache.set_authentication_id(authentication_name, authentication_id)
            except:
                conf.log.exception("Exception. get_authentication_id(%s) procedure call failed" %
                                   str(authentication_name))

        return authentication_id

    def create_authentication(self, authentication_name):
        try:
            with admin_transaction() as cursor:
                try:
                    query = "INSERT IGNORE INTO authentication(method) VALUES(%s)"
                    cursor.execute(query, authentication_name)
                except:
                    conf.log.exception("Exception. create_authentication(%s) query failed" %
                                       str(authentication_name))

                    # Re-raise the exception so that the context manager can roll back
                    raise
        except:
            # Return False on failure, but trust logging is used in context manager and
            # query execution
            return False

        return True


class AuthenticationEntity(object):
    """ Class for database authentication entities
    """

    def __init__(self):
        self.id = None
        self.name = None


class CQDEOrganizationStore(object):
    """ DAO for organizations
    """
    _instance = None

    def __init__(self):
        if CQDEOrganizationStore._instance:
            raise SingletonExistsException("Use CQDEOrganizationStore.instance()")
        self._helper = CQDEPermissionHelper.instance()
        self._cache = GroupPermissionCache.instance()

    @staticmethod
    def instance():
        if CQDEOrganizationStore._instance is None:
            CQDEOrganizationStore._instance = CQDEOrganizationStore()
        return CQDEOrganizationStore._instance

    def get_organizations(self):
        """ Returns a list of OrganizationEntity class instances
        """
        organizations = []
        with admin_query() as cursor:
            try:
                cursor.callproc("get_organizations")

                for row in cursor:
                    org = OrganizationEntity()
                    org.id = row[0]
                    org.name = row[1]
                    organizations.append(org)
            except:
                conf.log.debug("Exception. get_organizations procedure call failed.")

        return organizations

    def store_organization(self, organization):
        """ Stores organization into database
        """
        with admin_transaction() as cursor:
            try:
                query = "INSERT INTO organization (organization_name,sorting) VALUES (%s, %s)"
                cursor.execute(query, (organization.name, str(organization.sorting)))
            except:
                conf.log.exception("Exception. store_organization call failed.")
                raise

        return True

    def remove_organization(self, organization_name):
        """ Removes organization from database
        """
        self._cache.clear_organization_id(organization_name)
        # TODO: We need to clear organizationname / groupname cache for all
        # trac environments that have permissions for this organization (may be slow)
        return self._helper.call_proc_with_success("remove_organization", [organization_name])

    def get_organization_keys(self, user, auth_method=None):
        """
        Each authentication method has corresponding organization,
        which are applied to the user by default, when user is created
        """
        if not conf.organizations:
            return None

        if not auth_method:
            auth_store = CQDEAuthenticationStore.instance()
            auth_method = auth_store.get_authentication_method(user.authentication_key)

        organizations = []

        if auth_method:
            try:
                organization = conf.organizations[auth_method]
                if organization[1] == 'auths':
                    id = int(self.get_organization_id(organization[2]))
                    if id and id not in organizations:
                        organizations.append(id)
            except:
                conf.log.exception("Exception on auth_method")

        if user.mail:
            try:
                mailhost = "@" + user.mail.split("@")[1]
                organization = conf.organizations[mailhost]
                if organization[1] == 'email':
                    id = int(self.get_organization_id(organization[2]))
                    if id and id not in organizations:
                        organizations.append(id)
            except:
                conf.log.exception("Exception on user.mail")

        return organizations

    def get_organization_id(self, organization_name):
        organization_id = self._cache.get_organization_id(organization_name)
        if organization_id is not None:
            return organization_id

        with admin_query() as cursor:
            try:
                cursor.callproc("get_organization_id", [organization_name])
                row = cursor.fetchone()
                if row:
                    organization_id = row[0]
                    self._cache.set_organization_id(organization_name, organization_id)
            except:
                conf.log.exception("Exception. get_organization_id(%s) procedure call failed" %
                                   str(organization_name))
                raise

        return organization_id

    def get_organization_name(self, organization_id):
        organization_id = safe_int(organization_id)
        organization_name = self._cache.get_organization_name(organization_id)
        if organization_name is not None:
            return organization_name

        with admin_query() as cursor:
            try:
                query = "SELECT organization_name FROM organization WHERE organization.organization_id = %s"
                cursor.execute(query, organization_id)
                row = cursor.fetchone()
                if row:
                    organization_name = row[0]
                    self._cache.set_organization_name(organization_id, organization_name)
            except:
                conf.log.exception("Exception. get_organization_name(%s) failed" % str(organization_id))

        return organization_name


class OrganizationEntity(object):
    """ Class for database Organization entities
    """

    def __init__(self):
        self.id = None
        self.name = None
        self.sorting = None


class CQDELdapGroupStore(object):
    """
    DAO for LDAP groups
    """
    _instance = None

    def __init__(self):
        if CQDELdapGroupStore._instance:
            raise SingletonExistsException("Use CQDELdapGroupStore.instance()")
        self.__helper = CQDEPermissionHelper.instance()
        self.__cache = GroupPermissionCache.instance()

    @staticmethod
    def instance():
        if CQDELdapGroupStore._instance is None:
            CQDELdapGroupStore._instance = CQDELdapGroupStore()
        return CQDELdapGroupStore._instance

    def store_ldapgroup(self, ldapgroup_name):
        """ Stores ldap group into database
        """
        ldapgroup_name = ldapgroup_name.encode('utf-8')
        return self.__helper.call_proc_with_success("create_ldapgroup",
            [ldapgroup_name])

    def remove_ldapgroup(self, ldapgroup_name):
        """ Removes ldap group from database
        """
        self.__cache.clear_trac_environment_ldap_group_id(ldapgroup_name)

        return self.__helper.call_proc_with_success("remove_ldapgroup",
            [ldapgroup_name])

    def get_ldapgroup_id(self, ldapgroup_name):
        ldapgroup_id = self.__cache.get_trac_environment_ldap_group_id(ldapgroup_name)
        if ldapgroup_id is not None:
            return ldapgroup_id

        ldapgroup_id = None
        with admin_query() as cursor:
            try:
                cursor.callproc("get_ldapgroup_id", [ldapgroup_name])
                row = cursor.fetchone()
                if row:
                    ldapgroup_id = row[0]
                    self.__cache.set_trac_environment_ldap_group_id(ldapgroup_name, ldapgroup_id)
            except:
                conf.log.exception("Exception. get_ldapgroup_id(%s) procedure call failed" % str(ldapgroup_name))

        return ldapgroup_id


class CQDEPermissionPolicy(object):
    def check_permission(self, trac_environment_id, permission, check_username):
        """
        Helper class for the GlobalPermissionPolicy.check_permission,
        which checks also the resource, unlike this.
        Checks permission for the user in the trac environment.
        """
        # Disable completely features by appending actions into this list
        restricted_features = ['REPORT_CREATE', 'REPORT_SQL_VIEW']
        if permission in restricted_features:
            return False

        # Get user in question
        user_store = conf.getUserStore()
        user = user_store.getUser(check_username)
        store = CQDEUserGroupStore(trac_environment_id)
        superusers = CQDESuperUserStore.instance()

        # If there is no user then there is no need for permission check
        if not user:
            return False

        # Check if user is a superuser
        if superusers.is_superuser(user.username):
            return True

        # Get all permissions that grants this permission
        granting_permissions = self.get_granting_permissions(permission)

        # Get all groups and users
        user_groups = store.get_all_user_groups()
        group_perms = store.get_all_group_permissions()
        organization_groups = store.get_all_organization_groups()

        # List groups that have the permission
        groups = []
        for group, perm in group_perms:
            if perm in granting_permissions:
                groups.append(group)

        users = self.get_special_users(user.username)
        users.append(user.username)

        # See if user is in one of the groups
        for username, group in user_groups:
            if username in users:
                if group in groups:
                    return True

        # See if user's organization is in one of the groups
        org_store = CQDEOrganizationStore.instance()
        for org, group in organization_groups:
            org_id = org_store.get_organization_id(org)
            if org_id in user.organization_keys:
                if group in groups:
                    return True

        if conf.ldap_groups_enabled:
            # See if any ldap groups are allowed in environment
            auth_store = CQDEAuthenticationStore.instance()
            is_ldap_account = auth_store.is_ldap(user.authentication_key)
            trac_environment_ldapgroups = store.get_all_trac_environment_ldap_groups()
            if is_ldap_account and trac_environment_ldapgroups:
                # See if user belongs to any of the allowed ldap groups
                ldapuser_store = conf.getAuthenticationStore()
                user_ldapgroups = ldapuser_store.getGroups(user.username)
                for ldapgroup, group in trac_environment_ldapgroups:
                    if ldapgroup in user_ldapgroups:
                        if group in groups:
                            return True

        return False

    def get_granting_permissions(self, permission):
        """ Gives permissions that grants permission (except permission it's self)
        """
        # At least the permission it's self grants the permission
        granting_permissions = [permission]

        # Group *_VIEW, *_CREATE etc. to simple permissions
        groups = {}
        groups['DELETE'] = ['DELETE']
        groups['CREATE'] = ['CREATE', 'DELETE']
        groups['MODIFY'] = ['MODIFY', 'CREATE', 'DELETE']
        groups['VIEW'] = ['VIEW', 'MODIFY', 'CREATE', 'DELETE']

        # Hash table of permission => other granting permissions
        permissions = {}
        permissions['VERSION_CONTROL_VIEW'] = ['VERSION_CONTROL']
        permissions['WEBDAV_VIEW'] = ['WEBDAV']
        permissions['TICKET_CHGPROP'] = ['TICKET_MODIFY'] + groups['MODIFY']
        permissions['TICKET_APPEND'] = ['TICKET_MODIFY'] + groups['MODIFY']

        group = permission.split("_")[-1]
        if groups.has_key(group):
            granting_permissions.extend(groups[group])

        if permissions.has_key(permission):
            granting_permissions.extend(permissions[permission])

        # TRAC_ADMIN always grants permissions so append it into list if not already in
        if permission != 'TRAC_ADMIN':
            granting_permissions.append('TRAC_ADMIN')

        return granting_permissions

    def get_special_users(self, username):
        users = ['anonymous']
        if username and username != 'anonymous':
            users.append('authenticated')
        return users
