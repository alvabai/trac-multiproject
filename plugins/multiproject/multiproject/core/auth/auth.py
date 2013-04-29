# -*- coding: utf-8 -*-
from multiproject.core.authentication import CQDEAuthenticationStore
from multiproject.core.configuration import Configuration
conf = Configuration.instance()
from multiproject.core.users import User, get_userstore


class MultiprojectAuthentication(object):
    """ Interface for authentication plugins
    """

    def match(self, identifier):
        """ Returns True if plugin type matches to requested identifier string
            from conf.authentication_order.
        """
        return False

    def authenticate(self, user, password):
        """ Returns trac username if user is valid, None otherwise.
        """
        return None

    def get_trac_username(self, username):
        """ Returns real trac username - usually the same as parameter 'username',
            but in some cases (for example when authentication plugin allows
            logging in using email address) a different name.
        """
        return None

    def store_user_if_necessary(self, user):
        """
        Reads user information from authentication system and stores the data into local database.
        In case the user already exists in the local database, it is up to authentication system to decide
        where continue or not (return False or True)

        :returns:
            True if authentication backend managed to store user into userstore, otherwise False
            (code should continue to next backend)
        """
        return False

    def has_external_profile(self, user):
        """ Returns True if an external profile/icon is available for the user
        """
        return False


class Authentication(object):
    """
    """

    # Import authentication plugins.
    # Trac's ExtensionPoint system would be handy, but unfortunately it
    # depends on Environment which we don't want here.
    # Update: It depends on 1) Component, 2) ComponentManager,
    # 3) the module is imported. This would fix recursion errors on importing local_auth.py
    # Relates to 20120525000000_missing_organizations.py
    __auth_providers = []
    for item in conf.authentication_providers:
        try:
            components = item.strip().split('.')
            module_name = ".".join(components[:-1])
            class_name = components[-1]
            module = __import__(module_name, globals(), locals(), [class_name])
            klass = getattr(module, class_name)
            __auth_providers.append(klass())
        except Exception, e:
            conf.log.error("Error importing authentication module %s: %s" % (item, str(e)))
            pass

    def __init__(self):
        self.auth_store = CQDEAuthenticationStore.instance()
        self.primary_auth_method = conf.authentication_order[0].lower()

    def authenticate(self, username, password):
        """ Check username and password - either from local database, LDAP,
            or some other external authentication server.
            Return username on success, None on failure.
        """
        if not username or not password:
            return None

        # old user
        user = get_userstore().getUser(username)
        if user:
            authentication_name = self.auth_store.get_authentication_method(user.authentication_key)
            auth_module = self._get_auth_module(authentication_name)
            if auth_module:
                auth_username = auth_module.authenticate(username, password)
                if auth_username:
                    User.update_last_login(auth_username)
                    return auth_username
            return None

        # new user
        for x in conf.authentication_order:
            auth_module = self._get_auth_module(x)
            if auth_module:
                auth_username = auth_module.authenticate(username, password)
                if auth_username:
                    User.update_last_login(auth_username)
                    return auth_username
        return None

    def _get_auth_module(self, method):
        """
        Loops through all loaded authentication modules to find a matching one, based on
        method name.

        :param str method: Name of the method
        :returns: The corresponding authentication module or None
        """
        if method is None:
            return None

        for auth in self.__auth_providers:
            if auth.match(method):
                return auth

    def sync_user(self, username):
        """
        Iterates all the authentication providers and tries to store/create user against them (they return True if sync
        was completed successfully/implemented)

        Username may not yet exist; this tries to create a new account (i.e. for giving
        permissions to users who haven't yet logged in)

        :returns bool: True if user was synced successfully, otherwise False
        """
        for auth in self.__auth_providers:
            bename = auth.__class__.__name__

            # Stop when some auth plugin accepts username
            if auth.store_user_if_necessary(username):
                conf.log.info('Created user %s from backend: %s' % (username, bename))
                return True
            else:
                conf.log.debug('Skipped user creation with backend: %s' % bename)

        conf.log.warning('Failed to sync user %s with all of the auth backeds' % username)
        return False

    def get_trac_username(self, username):
        """
        Returns the username of the user existing in the local DB,
        which corresponds the given username.
        """
        # 1. Test first if username is already a real trac account name
        user = get_userstore().getUser(username)
        if user:
            return username

        # 2. Try auth plugins; some may allow e.g. mail address instead of username
        #    or case-insensitive authentication for username
        for auth_provider in self.__auth_providers:
            trac_username = auth_provider.get_trac_username(username)
            if trac_username:
                return trac_username

        # User not found
        return None

    def has_external_profile(self, user):
        if user:
            method = self.auth_store.get_authentication_method(user.authentication_key)
            auth = self._get_auth_module(method)
            if auth:
                return auth.has_external_profile(user)
        return False
