# -*- coding: utf-8 -*-
from multiproject.core.authentication import CQDEAuthenticationStore
from multiproject.core.configuration import conf
from multiproject.core.users import get_userstore, get_authstore
from multiproject.core.permissions import CQDEOrganizationStore, CQDELdapGroupStore
from multiproject.core.auth.auth import MultiprojectAuthentication


class LdapAuthentication(MultiprojectAuthentication):
    """
    Provides LDAP based authentication backend for Multiproject plugin
    """
    LDAP = 'LDAP'

    def __init__(self):

        self.org_store = CQDEOrganizationStore.instance()
        self.auth_store = CQDEAuthenticationStore.instance()
        self.ldap_authentication_key = self.auth_store.get_authentication_id(self.LDAP)
        if not self.ldap_authentication_key:
            self.auth_store.create_authentication(self.LDAP)
            self.ldap_authentication_key = self.auth_store.get_authentication_id(self.LDAP)
        if not self.ldap_authentication_key:
            # This should not happen
            raise Exception('LdapAuthentication: Could not get authentication id for LDAP')

    def match(self, identifier):
        return identifier.lower() == self.LDAP.lower()

    def authenticate(self, username, password):
        """
        Authenticates user against the LDAP server

        :param str username: Name of the user
        :param str password: Password of the user
        :returns:
            - SUCCESS: Name of the user
            - FAILURE: None
        """
        # NOTE: get_authstore returns the LDAP authentication store
        conf.log.debug('Trying LDAP authentication for %s' % username)
        ldap_store = get_authstore()

        orig_username = username
        trac_user = self._get_trac_user(username)
        trac_user_used_instead = False

        if trac_user and trac_user.username != orig_username:
            username = trac_user.username
            trac_user_used_instead = True

        if not ldap_store.userExists(username, password):
            if trac_user_used_instead:
                # trac_user and trac_user.username != orig_username
                username = orig_username
                if ldap_store.userExists(username):
                    # Should not happen, since LDAP userExists is case-insensitive
                    conf.log.warning("Case-sensitiveness mismatch in LDAP search: "
                                     "DB username '%s', LDAP username '%s'" % (trac_user.username, username))
            conf.log.debug('Failed to authenticate or find the user %s from LDAP' % username)
            return None

        ldap_store.reset_cache(username)

        # Existing user: check authentication_key
        if trac_user:
            if self.ldap_authentication_key != trac_user.authentication_key:
                # The user is authenticated by other authentication
                return None

        else:
            # there is always ldap_user, since it exists, unless it is removed at the same time
            # Thus, this will almost always success
            username = self._create_user(username)

        conf.log.info('Authenticated successfully against the LDAP: %s' % username)
        return username

    def store_user_if_necessary(self, username):
        """
        Store/sync user in local database from LDAP backend

        Does not do anything, if the user exists in the local DB.

        Used when the user, which does not yet exist in local DB, is added to group.
        Called by Authentication.sync_user, UserGroupsAdminPanel.add_users_to_group(s).

        :param str username: Name of the user to create
        :returns: True on success, False on failure
        """

        # If user already exists, no need to continue
        if get_userstore().userExists(username):
            return True

        # Try to create user from LDAP
        conf.log.debug('Trying to create user from LDAP')
        return self._create_user(username) is not None

    def _create_user(self, username):
        """
        Create new user using data available in LDAP service

        This method is used in two cases:
        - when the user is authenticated for the first time (by self.authenticate)
        - when the user, which doesn't yet exist in the local DB, is added to project group
          (by self.store_user_if_necessary)

        :param str username: Name of the user in LDAP
        :returns: username on success, otherwise None
        """
        users = get_userstore()
        ldap_store = get_authstore()

        # If user does not exists in LDAP, do not continue
        if not ldap_store.userExists(username):
            conf.log.debug('Cannot find user %s from LDAP' % username)
            return None

        # Create user using LDAP store
        user = ldap_store.getUser(username)
        user.authentication_key = self.ldap_authentication_key
        user.organization_keys = self.org_store.get_organization_keys(user, self.LDAP) or None

        # Store user in user store
        conf.log.info('Created new user from LDAP: %s' % user.username)
        users.storeUser(user)
        users.invalidate_user_password(user)

        return user.username

    def get_trac_username(self, username):
        """
        When this method is called, the search is already done with the username, without results.
        """
        user = self._get_trac_user(username)

        if user:
            return user.username
        return None

    def _get_trac_user(self, username):
        """
        :param str username: Name of the user in LDAP
        :returns: user from DB on success, otherwise None
        """
        # TODO: Should we use LDAP instead?
        userstore = get_userstore()

        query = """SELECT
                        user_id, username, mail, mobile, givenName, lastName,
                        icon_id, SHA1_PW, authentication_key,
                        user_status_key, last_login, created, expires, author_id
                     FROM user
                    WHERE username COLLATE utf8_general_ci = %s
                      AND authentication_key = %s """
        user_or_none = userstore.queryUser(query, (username, self.ldap_authentication_key))
        return user_or_none
