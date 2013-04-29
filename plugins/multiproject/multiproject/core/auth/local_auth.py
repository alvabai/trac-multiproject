# -*- coding: utf-8 -*-
from multiproject.core.authentication import CQDEAuthenticationStore
from multiproject.core.configuration import Configuration
conf = Configuration.instance()
from multiproject.core.auth.auth import MultiprojectAuthentication
from multiproject.core.users import get_userstore


class LocalAuthentication(MultiprojectAuthentication):
    LOCAL = "LocalDB"

    def __init__(self):

        self.auth_store = CQDEAuthenticationStore.instance()
        self.local_authentication_key = self.auth_store.get_authentication_id(self.LOCAL)
        if not self.local_authentication_key:
            self.auth_store.create_authentication(self.LOCAL)
            self.local_authentication_key = self.auth_store.get_authentication_id(self.LOCAL)
        if not self.local_authentication_key:
            # This should not happen
            raise Exception('LocalAuthentication: Could not get authentication id for LocalDB')

    def match(self, identifier):
        """
        Implementation to match this module against desired authentication module.

        See :py:class:`multiproject.core.auth.auth.MultiprojectAuthentication`
        """
        return identifier.lower() in ["local", "localdb"]

    def authenticate(self, username, password):
        """
        Authenticate users with local accounts

        :param str username: Name of the user
        :param str password: Password of the user
        :returns: Username of success, otherwise None
        """
        users = get_userstore()
        user = users.getUser(username)

        if user:
            if user.authentication_key != self.local_authentication_key:
                return None

            conf.log.debug('Trying local authentication for ' + username)
            if users.userExists(user.username, password):
                conf.log.info('Authenticated successfully against the local database: %s' % username)
                return username

        return None

    def store_user_if_necessary(self, username):
        """
        Store/sync user in local database from local authentication backend

        :param str username: Name of the user to create
        :returns: False (users aren't and can't be created just based username)
        """
        return False
