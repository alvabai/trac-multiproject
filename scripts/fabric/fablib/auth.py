# -*- coding: utf-8 -*-
"""
Contents of the module:

- AuthBackend: Abstract sudo authentication class
- PassFileAuthentication: Reads and authenticates with sudo based on password file location
- Auth: Authentication class that automatically selects one of the above

"""
__author__ = 'jumuston'
__all__ = ['Auth']

from fabric import api

from fablib.base import logger, config


class AuthBackend(object):
    """
    Abstract class for auth backends.
    """
    def authenticate(self, *args, **kwargs):
        pass


class PassFileAuthentication(AuthBackend):
    """
    Authentication backend for via txt file
    """
    def __init__(self, passfile):
        self.passfile = passfile


    def authenticate(self, env, *args, **kwargs):
        """
        Read the password from given file and sets
        it to Fabric env
        """
        sudo_pwd = self._read_sudo_password(self.passfile)
        if not sudo_pwd:
            return False
        env.password = sudo_pwd
        return True


    def _read_sudo_password(self, pwdfile):
        """
        Reads the sudo password from the specified location (expects the file contain nothing but password) and
        returns it back. If not found or password is empty, returns empty string
        """
        logger.debug('Using password file: %s' % pwdfile)
        with api.settings(api.hide('stdout', 'running')):
            pwd = api.run('cat %s' % pwdfile)
            return str(pwd.stdout).strip()


class Auth(AuthBackend):
    """
    Helper class to select correct authentication class based on configuration:

    - If sudo_password_path is defined, read sudo password from file (PassFileAuthentication)
    - If sudo_password_path is not defined, ask sudo password from user

    """
    def __new__(cls):
        auth = AuthBackend()
        sudo_password_path = config.get('sudo_password_path')
        if sudo_password_path:
            logger.debug('Reading sudo from file: %s' % sudo_password_path)
            auth = PassFileAuthentication(sudo_password_path)

        return auth
