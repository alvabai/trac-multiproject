# -*- coding: utf-8 -*-
from multiproject.core.configuration import conf
from multiproject.core.permissions import CQDEAuthenticationStore
from multiproject.core.auth.auth import MultiprojectAuthentication


class LocalAuthentication(MultiprojectAuthentication):

    def __init__(self):
        self.LOCAL = "LocalDB"
        self.auth_store = CQDEAuthenticationStore.instance()
        if not self.auth_store.get_authentication_id(self.LOCAL):
            self.auth_store.create_authentication(self.LOCAL)

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
        users = conf.getUserStore()
        user = users.getUser(username)

        if user:
            if not self.auth_store.is_local(user.authentication_key):
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
