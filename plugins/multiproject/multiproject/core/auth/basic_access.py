# -*- coding: utf-8 -*-
import base64
from datetime import datetime
import urllib, hashlib

from multiproject.core.permissions import CQDEPermissionPolicy
from multiproject.core.cache.permission_cache import AuthenticationCache
from multiproject.core.auth.auth import Authentication
from multiproject.core.users import User
from multiproject.core.configuration import conf
from multiproject.core.proto import ProtocolManager
from multiproject.core.util import env_id


class BasicAccessControl(object):
    """ Base class for creating access control with
        basic authentication

        If only authentication check is needed, can be
        used directly

        If permission check is needed, make a subclass
        and implement the needed methods
    """

    def __init__(self, req):
        self.req = req
        self.__cache = AuthenticationCache.instance()
        self.__auth = Authentication()
        self.parse_user_and_pw()
        self.options = req.get_options()

    def parse_user_and_pw(self):
        self._username = "anonymous"
        self._password = ""

        if 'Authorization' in self.req.headers_in:
            # Authorization: Basic <base64 username and pw>
            authz_hdr = base64.b64decode(self.req.headers_in['Authorization'].split(' ')[1])
            user_data, pw_data = authz_hdr.split(':',1)
            self._username = urllib.unquote(user_data)
            encoded_password = urllib.unquote(pw_data)
            resulting_password = ''
            try:
                resulting_password = encoded_password.decode('UTF-8')
            except UnicodeDecodeError as e:
                try:
                    resulting_password = encoded_password.decode('ISO-8859-1')
                except UnicodeDecodeError as e:
                    # Should not happen, since for ISO-8859-1, every string
                    # is a valid string
                    conf.log.error('Password conversion from ISO-8859-1 FAILED')
            self._password = resulting_password
            self.req.user = self.username

        if not self._username:
            self._username = "anonymous"
            self._password = ""

    def is_authentic(self):
        """ Check that user really exists
        """
        username = self.username
        plain_pw = self.plain_pw

        # Anonymous is always authentic
        auth_anonymous = 'auth_anonymous' in self.options
        if auth_anonymous and username == 'anonymous':
            return True

        # Compare database hash and computed hash
        hash = hashlib.sha1(plain_pw).hexdigest()
        auth_username = self.__cache.getAuthentication(username, hash)

        if not auth_username:
            auth_username = self.__auth.authenticate(username, plain_pw)
            self.__cache.setAuthentication(username, hash, auth_username)

        is_auth = False
        if auth_username is not None:
            self._username = auth_username
            auth_encoded = auth_username.encode('utf-8')
            # Don't know why req.username is set
            self.req.username = auth_encoded
            # At least in git.py, req.user was set to be the username
            self.req.user = auth_encoded
            is_auth = True

        return is_auth

    def has_permission(self):
        if not self.environment_identifier():
            conf.log.warning("Failed reading identifier")
            return False

        policy = CQDEPermissionPolicy()
        had = policy.check_permission(self.environment_key,
            self.required_action,
            self.username)
        return had

    def is_blocked(self):
        """
        Check if user account is blocked/expired or not. In a case of anonymous user,
        it's never blocked.

        .. NOTE:

           Uses internally the self.username

        :returns: True if blocked (inactive, banned, disabled or expired)
        """
        # Anonymous user is never blocked
        if self.username == 'anonymous':
            return False

        userstore = conf.getUserStore()
        user = userstore.getUser(self.username)

        if user.expires and user.expires <= datetime.utcnow():
            return True

        if user.status not in [User.STATUS_ACTIVE]:
            return True

        return False


    def is_allowed_scheme(self, system):
        if not conf.use_protocol_check:
            return True

        protos = ProtocolManager(self.environment_key)
        scheme = self.req.construct_url('/').split(':')[0]
        return protos.is_protocol_allowed(scheme, system)

    @property
    def required_action(self):
        if self.is_read():
            return self.read_action()
        return self.write_action()

    @property
    def environment_key(self):
        return env_id(self.environment_identifier())

    @property
    def plain_pw(self):
        return self._password

    @property
    def username(self):
        return self._username

    # Helper for subclasses
    def parse_identifier_from_uri(self):
        """
        Tries to parse the project identifier from request URI.
        Example URI values:

        - /dav/projectx
        - /dav/projectx/file.txt
        - /dav/projectx/sub/folder/file.txt

        .. IMPORTANT::

            Check also for /dav/haxor.txt

        :returns: Project identifier or None
        """
        identifier = None

        # Drop leading slash so we'll have: items[0] == 'dav'
        uri = self.req.uri[1:] if self.req.uri.startswith('/') else self.req.uri
        items = uri.split('/', 3)
        # Strip empty elements
        items = [item for item in items if item]

        # If less than 2 elements, no identifier cannot be found
        if len(items) < 2:
            conf.log.warning('Failed to parse project identifier from URI: %s' % uri)
            return None

        # Identifier is always expected to be second (index 0) element.
        # If identifier contains the multirepo separator (default: '.'), return the first part
        identifier = items[1]

        if conf.multirepo_separator in identifier:
            identifier = identifier.split(conf.multirepo_separator)[0]

        return identifier

    #
    # Abstract methods for subclasses that needs
    # permission checking
    #
    def environment_identifier(self):
        """ Subclass needs to implement this
        """
        raise NotImplementedError

    def is_read(self):
        """ Subclass needs to implement this
        """
        raise NotImplementedError

    def read_action(self):
        """ Subclass needs to implement this
        """
        raise NotImplementedError

    def write_action(self):
        """ Subclass needs to implement this
        """
        raise NotImplementedError
