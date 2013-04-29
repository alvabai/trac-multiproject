"""
User model and related backend implementations.
"""
from contextlib import contextmanager
from datetime import datetime
import ldap
import ldap.filter
import unicodedata
from trac.perm import PermissionCache

try:
    from hashlib import sha1 as sha
except ImportError:
    from sha import sha

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from multiproject.core.configuration import Configuration
conf = Configuration.instance()
from multiproject.core.util.ldaphelper import get_search_results
from multiproject.core.cache.user_cache import UserCache
from multiproject.core.cache.permission_cache import AuthenticationCache
from multiproject.core.cache.permission_cache import GroupPermissionCache
from multiproject.core.db import admin_transaction, admin_query, safe_string, safe_int
from multiproject.core.authentication import CQDEAuthenticationStore


# Formatting rules for python and javascript: 25/01/12
DATEFORMATS = {
    'py': '%m/%d/%y',
    'pydt': '%m/%d/%y %H:%m',
    'js': 'mm/dd/y'
}


# This module contains api classes for user management
class User(object):
    """ User class for holding user information
    """
    STATUS_INACTIVE = 1
    STATUS_ACTIVE = 2
    STATUS_BANNED = 3
    STATUS_DISABLED = 4

    def __init__(self):
        self.id = None
        self.username = None
        self.password = None
        self.pwHash = None
        self.mail = None
        self.mobile = None
        self.givenName = None
        self.lastName = None
        self.icon = None
        self.authentication_key = None
        self.status = None
        self.last_login = None
        self.created = None
        self.expires = None
        self.author_id = None
        self.preferences = {}
        self.organization_keys = []

    def __repr__(self):
        """ Returns readable presentation from the User object
        """
        return '<User %s: %s>' % (self.id, self.getDisplayName())

    def __unicode__(self):
        """
        Returns string presentation from the user
        """
        return self.getDisplayName()

    def __json__(self):
        """
        Returns dict presentation of the object, ready
        for JSON encoding
        """
        return {
            'id': self.id,
            'username': self.username,
            'displayname': self.getDisplayName(),
            'firstname': self.givenName,
            'lastname': self.lastName,
            'avatar_url': self.getAvatarUrl(),
        }

    def getDisplayName(self):
        """ Returns name that can be displayed on web.
            Configuration file tells which of username, firstname, lastname or mail address
            are included in the display name.
        """
        display_name = []
        for element in conf.display_name:
            if element == "username" and self.username:
                display_name.append(self.username)
            elif element == "firstname" and self.givenName:
                display_name.append(self.givenName)
            elif element == "lastname" and self.lastName:
                display_name.append(self.lastName)
            elif element == "mail" and self.mail:
                display_name.append(self.mail)
            elif element in ["(", ")", " "]:
                display_name.append(element)

        if not display_name:
            display_name = self.username
        else:
            display_name = "".join(display_name)

        return display_name

    def createIcon(self, icon):
        """ Creates icon for user based on icon sent on create form
            TODO: This should be on MySQLUserStore
        """
        # FIXME: Move user icon into filesystem for better performance, similar to project icon
        self.icon = None
        if isinstance(icon, unicode) or not icon.filename:
            return
        content_type = icon.type

        with admin_transaction() as cursor:
            try:
                cursor.execute("INSERT INTO user_icon VALUES(null, '" + safe_string(
                    icon.value) + "', '" + safe_string(content_type) + "')")

                # Resolve last inserted icon id
                cursor.execute("SELECT last_insert_id() FROM user_icon")
                row = cursor.fetchone()
                if row:
                    if row[0] != 0:
                        # If nonzero is returned, row was successfully added
                        self.icon = row[0]
            except:
                conf.log.exception("Exception. Failed creating icon.")
                raise

    def activate(self):
        query = ("UPDATE user SET user_status_key = %s "
                 "WHERE user.user_id = %s LIMIT 1")

        with admin_transaction() as cursor:
            try:
                cursor.execute(query, (self.STATUS_ACTIVE, self.id))
            except:
                conf.log.exception("Exception. Failed activating user with query '''%s'''." % query)
                raise

        UserCache.instance().clear_user_by_user(self)

        self.status = self.STATUS_ACTIVE
        return self.status

    def getAvatarUrl(self, size=40):
        from multiproject.core.auth.auth import Authentication

        auth = Authentication()
        if auth.has_external_profile(self):
            return conf.external_avatar_url + self.username + "&size=" + str(size)
        elif self.icon:
            return conf.url_home_path + "/usericon?username=" + self.username
        else:
            return conf.theme_htdocs_location + "/images/no_icon.gif"

    def can_create_project(self):
        """
        .. WARNING:: This may be expensive call because it opens home project environment!

        :return: Boolean
        """
        # Avoid circular imports
        from multiproject.common.projects import HomeProject

        homeenv = HomeProject().get_env()
        homeperm = PermissionCache(homeenv, username=self.username)
        return 'PROJECT_CREATE' in homeperm

    @staticmethod
    def update_last_login(username):
        """ Updates user's last login timestamp to user table
        """
        if not username:
            return

        query = "UPDATE user SET last_login=NOW() WHERE user.username='%s'" % safe_string(username)
        with admin_transaction() as cursor:
            try:
                cursor.execute(query)
            except:
                conf.log.exception("Query failed: %s" % query)
                raise


class UserStore(object):
    """ Base class for different user stores
    """

    def getUser(self, username):
        """ Get user by username
        """
        pass

    def storeUser(self, user):
        """ Stores a new user
        """
        pass

    def deleteUser(self, user):
        """ Deletes a user
        """
        pass

    def updateUser(self, user):
        """ Updates user info
        """
        pass

    def userExists(self, username, password=None):
        """ Check that user exists on store
            Check that user is who he/she claims to be if password given
        """
        pass

    def is_local(self, user):
        """
        Check if given user is local or not
        :returns: True if user is a local user, otherwise False
        """
        raise NotImplementedError()


class MySqlUserStore(UserStore):
    """ User store to write users into persistent mysql database
    """

    def __init__(self):
        self.__cache = UserCache.instance()
        self.__authcache = AuthenticationCache.instance()
        self.USER_STATUS_LABELS = {
            User.STATUS_INACTIVE: 'inactive',
            User.STATUS_ACTIVE: 'active',
            User.STATUS_BANNED: 'banned',
            User.STATUS_DISABLED: 'disabled'
        }
        # Provide also opposite mapping: {'inactive':User.STATUS_INACTIVE}
        self.USER_STATUS_KEYS = dict((v, k) for k, v in self.USER_STATUS_LABELS.items())

    def getUser(self, username):
        """
        Get user from memcached or from database by username, if not present in
        memcached.

        :param str username: User login name
        :returns: The User object or None
        """

        conf.log.debug('Getting user "{0}"'.format(username))

        user = self.__cache.getUser(username)
        if user is not None:
            return user

        if not user:
            query = '''
            SELECT
                user_id, username, mail, mobile, givenName, lastName,
                icon_id, SHA1_PW, authentication_key, user_status_key,
                last_login, created, expires, author_id
            FROM user
            WHERE username = %s
            '''

            user = self.queryUser(query, (username,))
            if user:
                self.fetchUserOrganizations(user)
                self.fetchUsersPreferences(user)  # update user preferences inside user object
                self.__cache.setUser(user)

        return user

    def fetchUsersPreferences(self, user):
        """ Get users preferences
        """
        if user is None:
            return

        query = "SELECT item, value FROM user_preference "
        query += "WHERE user_key = %d" % safe_int(user.id)

        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    user.preferences[row[0]] = row[1]
            except:
                conf.log.exception("Exception. User preferences query failed '''%s'''." % query)
                raise

    def fetchUserOrganizations(self, user):
        """ Get users preferences
        """
        if user is None:
            return

        organization_keys = []

        query = '''
        SELECT organization_key
        FROM user_organization
        WHERE user_key = %s
        '''

        with admin_query() as cursor:
            try:
                cursor.execute(query, safe_int(user.id))
                for row in cursor:
                    organization_keys.append(row[0])
                user.organization_keys = organization_keys
            except:
                conf.log.exception("Exception. User organizations query failed '''%s'''." % query)
                raise

    def getUserWhereId(self, user_id):
        """
        Get user from user store with id

        .. NOTE::

            Reads and writes from cache, where cache key is constructed from user id
            Preferences are not populated

        :param int user_id: User id
        :returns: User from cache - or None if not found
        :rtype: User
        """
        # Read from cache
        user = self.__cache.getUser(user_id)
        if user:
            return user

        # Read from database
        query = '''
        SELECT
            user_id, username, mail, mobile, givenName, lastName,
            icon_id, SHA1_PW, authentication_key,
            user_status_key, last_login, created, expires, author_id
        FROM user
        WHERE user_id = %s
        '''

        user = self.queryUser(query, (user_id,))
        if not user:
            return None

        self.fetchUserOrganizations(user)
        self.fetchUsersPreferences(user)  # update user preferences inside user object
        self.__cache.setUser(user)
        return user

    def queryUser(self, query, params=None):
        """ Method for creating user object from mysql query
        """
        conf.log.debug('Querying user with params {0}'.format(params))
        with admin_query() as cursor:
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                row = cursor.fetchone()
                if row:
                    return MySqlUserStore.sqlToUser(row)
            except:
                conf.log.exception("Exception. User query failed '''%s'''." % query)
                raise

    def query_users(self, query):
        users = []
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    users.append(MySqlUserStore.sqlToUser(row))
            except:
                conf.log.exception("Exception. query_users failed '''%s'''." % query)
                raise

        return users

    def get_user_author(self, user):
        """
        Returns the user author object, if the user has one
        """
        if not user.author_id:
            return None
        return self.getUserWhereId(user.author_id)

    @staticmethod
    def sqlToUser(row):
        """
        Dataset fetch from SQL statement to User object
        """
        user = User()
        user.id = row[0]
        user.username = unicode(row[1])
        user.mail = unicode(row[2])
        user.mobile = unicode(row[3])
        user.givenName = unicode(row[4])
        user.lastName = unicode(row[5])
        user.icon = row[6] or None
        user.pwHash = unicode(row[7])
        user.authentication_key = row[8]
        user.status = row[9]
        user.last_login = row[10]
        user.created = row[11]
        user.expires = row[12]
        user.author_id = row[13]

        return user

    def storeUser(self, user):
        """
        Function for writing user into persistent storage

        .. IMPORTANT::

            Function also saves the password hash into database.
            If non-local user, pw hash will be 'invalidNonLocalUserPwHash'.

        :returns: True on success, False on failure
        """
        self.__cache.clearUser(user.username)

        # Set defaults for optional fields
        user.mobile = user.mobile or ''
        user.password = user.password or ''
        user.givenName = user.givenName or ''
        user.lastName = user.lastName or ''
        user.icon = safe_int(user.icon) or None
        user.created = user.created or datetime.utcnow()
        user.expires = user.expires or None  # By default, no expire date
        user.author_id = user.author_id or None  # By default, no author/owner information

        # Check the required fields: username and password
        if not user.username:
            conf.log.error('User object is missing username - giving up user store')
            return False

        auth_store = CQDEAuthenticationStore.instance()
        local_authentication_key = auth_store.get_authentication_id(auth_store.LOCAL)

        if not user.authentication_key:
            user.authentication_key = local_authentication_key

        # Set default status id based on name defined configuration
        default_status_name = conf.default_user_status.lower()
        status_key = self.USER_STATUS_KEYS.get(default_status_name)
        if not status_key:
            self.log.error('Failed to find and set user default status')
            return False

        sha1_pw = 'SHA1(%s)'
        if user.authentication_key != local_authentication_key:
            user.password = 'invalidNonLocalUserPwHash'
            sha1_pw = '%s'

        # SQL query for creating a new user
        query = """
        INSERT INTO user (
            user_id, username, mail, mobile, givenname, lastname, created,
            icon_id, SHA1_PW, authentication_key, user_status_key,
            expires, author_id
        )
        VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, {sha1_pw}, %s, %s, %s, %s)
        """.format(sha1_pw=sha1_pw)

        # SQL params
        params = (
            user.username, user.mail, user.mobile,
            user.givenName.encode('utf-8'), user.lastName.encode('utf-8'), user.created, user.icon,
            user.password.encode('utf-8'), str(user.authentication_key), str(status_key),
            user.expires, user.author_id
        )

        with admin_transaction() as cursor:
            try:
                cursor.execute(query, params)
                user.id = cursor.lastrowid
            except:
                conf.log.exception("Failed to create user")
                raise

        self.storeUserOrganizations(user)
        self.updateUserPreferences(user)

        return True

    def storeUserOrganizations(self, user):
        with admin_transaction() as cursor:
            try:
                query = "DELETE FROM user_organization WHERE user_key = " + str(safe_int(user.id))
                cursor.execute(query)
                if not user.organization_keys:
                    return
                query = "INSERT INTO user_organization (user_key, organization_key) VALUES "
                pairs = []
                for organization_id in user.organization_keys:
                    pairs.append("(" + str(safe_int(user.id)) + ", " +
                                 str(safe_int(organization_id)) + ")")
                query += ",".join(pairs)
                conf.log.debug(query)
                cursor.execute(query)
            except:
                conf.log.exception("Exception. update of user organizations failed '''%s'''." % query)
                raise

    def updateUserPreferences(self, user):
        with admin_transaction() as cursor:
            try:
                for item, value in user.preferences.iteritems():
                    query = "INSERT INTO user_preference (user_key, item, value) VALUES ("
                    query += (str(safe_int(user.id)) + ", '" + safe_string(item)
                              + "', '" + safe_string(str(value)) + "') ")
                    query += "ON DUPLICATE KEY UPDATE value = '" + safe_string(str(value)) + "'"
                    cursor.execute(query)
            except:
                conf.log.exception("Exception. update of user preferences failed '''%s'''." % query)
                raise

        return True

    def deleteUser(self, user):
        """ Function for removing user from persistent storage
        """
        self.__cache.clear_user_by_user(user)
        query = "DELETE FROM user WHERE user_id = %s"
        with admin_transaction() as cursor:
            try:
                cursor.execute(query, user.id)
            except:
                conf.log.exception('Failed to delete the user: %s' % user)
                return False

        return True

    def updateUser(self, user):
        """
        Updates user but not a password.
        There is a separate method for updating password
        """
        self.__cache.clear_user_by_user(user)

        user.icon = safe_int(user.icon) or None

        # FIXME: Usernames can not be changed. Unnecessary update?
        query = '''
        UPDATE user
        SET
            username = %s, mail = %s, mobile = %s, givenName = %s, lastName = %s, icon_id = %s,
            authentication_key = %s, user_status_key = %s, created = %s, expires = %s, author_id = %s
        WHERE user_id = %s
        '''
        params = (
            user.username, user.mail, user.mobile, user.givenName.encode('utf-8'), user.lastName.encode('utf-8'),
            user.icon, str(user.authentication_key), str(user.status), user.created,
            user.expires, user.author_id, user.id
        )

        with admin_transaction() as cursor:
            try:
                cursor.execute(query, params)
            except:
                conf.log.exception("Exception: updating user failed '''%s'''." % query)
                raise

        self.storeUserOrganizations(user)
        return self.updateUserPreferences(user)

    def updatePassword(self, user, password):
        """ Changes user password into given raw password
        :param User user: user to be updated (id must be set)
        :param str password: password either ordinary or unicode string
        """
        self.__cache.clear_user_by_user(user)

        if not password:
            return False
        if not user.id:
            return False

        # Do update
        with admin_transaction() as cursor:
            try:
                cursor.execute("SELECT SHA1_PW FROM user WHERE user_id = %s", user.id)
                sha = cursor.fetchone()
                # TODO: move str(sha[0]) part into the clearAuthentication method
                self.__authcache.clearAuthentication(user.username, str(sha[0]).encode('utf-8'))
                cursor.execute("UPDATE user SET SHA1_PW = SHA1(%s) WHERE user_id = %s",
                               (password.encode('utf-8'), user.id))
            except Exception:
                conf.log.exception("Failed to update password.")
                return False
        return True

    def invalidate_user_password(self, user):
        """
        Changes the user password to 'invalidNonLocalUserPwHash' for non-local user
        Clears caching as in updatePassword

        .. Note ::

            Used only for non-local users!
            SHA1_PW must not contain space characters, since it is used in memcache key

        """
        self.__cache.clear_user_by_user(user)

        if not user.id:
            return False
        from multiproject.core.authentication import CQDEAuthenticationStore
        auth_store = CQDEAuthenticationStore.instance()
        query = """UPDATE `user`
               INNER JOIN authentication ON `user`.authentication_key = authentication.id
                      SET `user`.SHA1_PW = 'invalidNonLocalUserPwHash'
                    WHERE user_id = %s
                      AND authentication.method <> %s"""

        result = True
        # Do invalidation
        with admin_transaction() as cursor:
            try:
                cursor.execute("SELECT SHA1_PW FROM user WHERE user_id = %s", user.id)
                sha = cursor.fetchone()
                self.__authcache.clearAuthentication(user.username, str(sha[0]).encode('utf-8'))
                if sha[0] != 'invalidNonLocalUserPwHash':
                    # If not already invalid password hash
                    cursor.execute(query, (user.id, auth_store.LOCAL))
                    if not cursor.rowcount:
                        conf.log.error("Nothing affected when invalidating password for user %s"
                                       % user.username)
                        result = False
            except Exception:
                conf.log.exception("Failed to invalidate password for user %s." % user.username)
                return False
        return result

    def update_user_email(self, user, email=None):
        """
        Updates user email address.
        :param str email: when given, updates only when different from user.mail
        """
        if email is not None:
            if user.mail == email:
                return
            else:
                user.mail = email

        self.__cache.clear_user_by_user(user)
        # TODO: Update also the email in global and project-specific session(s)

        query = '''
        UPDATE user
           SET mail = %s
         WHERE user_id = %s
        '''

        with admin_transaction() as cursor:
            try:
                cursor.execute(query, (user.mail, user.id))
            except:
                conf.log.exception("Exception: updating user failed '''%s'''." % query)
                raise

    def update_user_status(self, user, status_id):
        """
        Updates the user status based on given status key. Use mapping fournd in userstore::

            userstore = get_userstore()
            userstore.update_user_status(user, userstore.USER_STATUS_LABELS['banned'])

        :param int status_id: Status id (if not given, status_label must be given)
        :return True on success, False
        """
        if status_id not in self.USER_STATUS_LABELS.values():
            raise Exception('Unknown status id')

        user.status = status_id
        return self.updateUser(user)

    def _compare_password(self, user, password):
        """ Compares raw password to stored value
        """
        shaobj = sha(password.encode('utf-8'))
        hexsha = shaobj.hexdigest()
        match = (user.pwHash == hexsha.lower())

        if not match:
            conf.log.warning("User %s password stored in %s does not match given" %
                             (user.username, self.__class__.__name__))

        return match

    def userExists(self, username, password=None):
        """ Check that user exists in persistence
            If password given, it must also match ow. False
        """
        user = self.getUser(username)

        # No user
        if not user:
            return False

        # If password was given check it
        if password is not None:
            return self._compare_password(user, password)
        else:
            return True

    def is_local(self, user):
        """
        Check if given user is local or not
        :param User user: User to check
        :returns: True if user is a local user, otherwise False
        """
        from multiproject.core.authentication import CQDEAuthenticationStore
        auth_store = CQDEAuthenticationStore.instance()
        return auth_store.is_local(user.authentication_key)

    def get_user_initials(self):
        """ List all initial letters in usernames in uppercase
            Also returns counts of the initials
        """
        query = "SELECT UPPER(SUBSTRING(username, 1,1)) AS initial, count(*) AS count "
        query += "FROM user WHERE UPPER(SUBSTRING(username, 1,1)) != ' ' "
        query += "AND username NOT IN ('authenticated', 'anonymous') "
        query += "GROUP BY initial"

        initials = []
        initial_counts = {}
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    initial = row[0]
                    count = row[1]
                    initials.append(initial)
                    initial_counts[initial] = count
            except:
                conf.log.exception("Exception. Failed with user initials query '''%s'''." % query)
                raise

        return initials, initial_counts

    def get_all_users(self, limit=0, count=50, initial=None):
        """ List all users

            If no parameters given, lists first 50 users.
            If limit given, lists first 50 users from the limit.
            If initial given, lists only users having that initial.
        """
        query = "SELECT username, givenName, lastName, mail, mobile FROM user "
        query += "WHERE username NOT IN ('authenticated', 'anonymous') "
        if initial:
            query += "AND (username LIKE '" + safe_string(initial[0].upper()) + "%' "
            query += "OR username LIKE '" + safe_string(initial[0].lower()) + "%') "
        query += "ORDER BY username LIMIT %d,%d" % (safe_int(limit), safe_int(count))

        users = []
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for user in cursor:
                    s = {'username': user[0],
                         'first': user[1],
                         'last': user[2],
                         'email': user[3],
                         'mobile': user[4]}
                    users.append(s)
            except:
                conf.log.exception("Exception. Users.get_all_users query failed '''%s'''." % query)
                raise

        return users

    def get_all_usernames(self):
        query = "SELECT username FROM user"
        users = []

        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    users.append(row[0])
            except:
                conf.log.exception("Query for usernames failed")

        return users

    def get_expired_users(self, when=None):
        """
        Returns users that accounts are expired, or will soon expire (if when date is in future)

        :param datetime when: Date in future, other wise returns the accounts that are already expired
        :returns: List of user objects
        """
        users = []
        when = when or datetime.utcnow()

        query = """
        SELECT user.*
        FROM user
        LEFT JOIN user_status ON user_status.user_status_id = user.user_status_key
        WHERE
            user.expires <= %s AND
            LOWER(user_status.status_label) != 'banned'
        ORDER BY user.expires DESC
        """

        with admin_query() as cursor:
            cursor.execute(query, when)
            for row in cursor:
                users.append(self.sqlToUser(row))

        return users

    def getUserCount(self):
        """ Get user count from user store
        """
        query = "SELECT count(*) FROM user"

        row = None

        with admin_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
            except:
                conf.log.exception("Exception. Users.getUserCount query failed.")

        if row:
            return row[0]

        return 0

    def getMemberCountInProjects(self):
        """ Get user count that are members in projects from user store
        """
        member_count = self.__cache.getTotalMemberCount()
        if member_count:
            return member_count

        query = "SELECT COUNT(DISTINCT user_key) FROM user_group"

        row = None

        with admin_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
            except:
                conf.log.exception("Exception. Users.getMemberCountInProjects query failed.")

        if row:
            self.__cache.setTotalMemberCount(row[0])
            return row[0]

        return 0

    def get_emails(self, usernames):
        if not usernames:
            return []
        usernames_wrapped = []
        for username in usernames:
            usernames_wrapped.append("'" + safe_string(username) + "'")
        usernames_str = ','.join(usernames_wrapped)

        mails = []
        query = "SELECT DISTINCT mail FROM user WHERE username IN (" + usernames_str + ")"

        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    if '@' in row[0]:
                        mails.append(row[0])
            except:
                conf.log.exception("Exception. Query failed when getting emails '''%s'''" % query)
                raise

        return mails


class LdapUserStore(UserStore):
    """
    User store for storing user information into LDAP
    Only supported connection mode is simple_bind. Thus, following methods **are not supported**:

    - SASL
    - TSL

    LDAP connection are automatically created and closed for actions that needs it.
    For the connection, there is both decorator :meth`ldapconnection` and context `ldapcontext`
    for nice API.
    """
    def __init__(self):
        """
        Initializes LDAP-connection
        """
        # Read connection configuration info from conf
        self.connectPath = conf.ldap_connect_path

        # Admin rights are needed at least for creating users
        self.username = conf.ldap_bind_user
        self.password = conf.ldap_bind_password

        # Read other info from conf
        self._group_dn = conf.ldap_groups_dn
        self._group_cn = conf.ldap_groups_cn
        self._uid = conf.ldap_uid
        self._user_rdn = conf.ldap_user_rdn
        self._base_dn = conf.ldap_base_dn
        self._object_classes = conf.ldap_object_classes

        self._connection = None

        self.__cache = GroupPermissionCache.instance()

    def _connect(self, username=None, password=None):
        """
        Initializes and binds the LDAP connection

        :param str username:
            Name of user with bind with. Defaults to configuration values.

            .. NOTE:: Username is in LDAP format like::

                username = 'cn=admin, dc=it, dc=local'


        :param str password: Password of user with bind with. Defaults to configuration values.
        :returns: None
        """
        username = username or self.username
        password = password or self.password

        conf.log.debug('Connecting to LDAP (%s) with %s account: %s' %
                       (self.connectPath, 'provided' if username else 'configured', username))

        # Initialize ldap connection
        try:
            # Connect with LDAP using protocol version 3
            self._connection = ldap.initialize(self.connectPath)
            self._connection.protocol_version = ldap.VERSION3

            # Bind with LDAP
            if username and password:
                self._connection.simple_bind_s(username, password)
            else:
                self._connection.simple_bind_s()

        except:
            conf.log.exception("Failed to connect with LDAP: %s" % self.connectPath)
            raise

    def _close(self):
        """
        Closes the connection with the LDAP directory
        """
        if not self._connection:
            return

        try:
            conf.log.debug('Closing the to LDAP connection')
            self._connection.unbind()
        except Exception:
            conf.log.exception("Failed to close LDAP connection. Setting it None anyway")
        finally:
            self._connection = None

    def ldapconnection(ldapfn):
        """
        Decorator for creating and closing the LDAP connection

        >>> @ldapconnection
        >>> def myfunc(self):
        >>>     # Do something with connection

        :returns: Output of the LDAP action
        :raises: Exception in a case of issues
        """
        def decorator(self, *args, **kwargs):
            conf.log.debug('LDAP connection required by %s' % ldapfn.__name__)
            try:
                self._connect()
                out = ldapfn(self, *args, **kwargs)
                self._close()
            except Exception:
                conf.log.exception('Failed execute LDAP action: %s' % ldapfn.__name__)
                raise

            return out

        return decorator

    @contextmanager
    def ldapcontext(self):
        """
        Context for LDAP connection, to be used *with* keyword:

        >>> def myfunc(self):
        >>>   # Do something with connection
        >>>   with self.ldapcontext:
        >>>      self._connection.add_s(user_dn, user_record)
        >>>
        >>>   # Connection is automatically closed after
        """
        try:
            self._connect()
            yield
            self._close()
        except Exception:
            conf.log.exception('Failed execute LDAP action')
            raise

    @ldapconnection
    def getUser(self, username):
        """
        Gets user object from LDAP

        :param str username: Name of the LDAP user
        """
        # Attribute mappings between LDAP and UserStore
        # In case of multiple keys, secondary are the fallbacks
        regfields = {
            'username': [self._uid],
            'lastName': ['sn', 'surname'],
            'mail': ['mail'],
        }
        optfields = {
            'gn': ['gn'],
            'givenName': ['givenName'],
            'mobile': ['mobile'],
        }
        # Since the pwHash contains non-hex characters, MySqlUserStore._compare_password
        # always returns False
        default_fields = {
            'pwHash': 'invalidNonLocalUserPwHash',
        }

        userdata = self._search_user(username)
        if userdata:
            # Start building a user
            user = User()
            user.id = None

            # Handle required fields
            for fname, fkeys in regfields.items():
                fvalue = None
                for fkey in fkeys:
                    if userdata.has_attribute(fkey):
                        fvalue = userdata.get_attr_values(fkey)[0]
                        break

                # If no value was found, raise an issue. Otherwise store the value
                if not fvalue:
                    raise Exception('Insufficient LDAP user information: "%s:%s" missing for account "%s"' % (fname, fkeys, username))

                setattr(user, fname, fvalue)

            # Update optional fields is optional
            for fname, fkeys in optfields.items():
                fvalue = None
                for fkey in fkeys:
                    if userdata.has_attribute(fkey):
                        fvalue = userdata.get_attr_values(fkey)[0]

                # Store the value
                if fvalue:
                    setattr(user, fname, fvalue)

            # Set default values for default fields
            for fname, fvalue in default_fields.items():
                setattr(user, fname, fvalue)

            return user
        else:
            return None

    @ldapconnection
    def storeUser(self, user):
        """
        Stores user object into LDAP
        """
        # Don't add if user exist
        if self.userExists(user.username):
            return False

        user_record = self._createUserRecord(user)
        user_dn = self._createUserDn(user)
        try:
            self._connection.add_s(user_dn, user_record)
        except ldap.LDAPError, e:
            conf.log.error(e.message['info'])

        return True

    @ldapconnection
    def deleteUser(self, user):
        """
        Removes user from LDAP
        """
        try:
            self._connection.delete(self._createUserDn(user))
        except Exception:
            return False
        return True

    def reset_cache(self, username):
        """
        Clears LDAP cache for specific user
        """
        conf.log.debug('Clearing LDAP user group cache for: %s' % username)
        return self.__cache.clear_user_ldap_groups(username)

    def _createUserDn(self, user):
        """
        Creates dn for user based on configuration information
        """
        user_dn = self._uid + '=' + user.username
        if self._user_rdn:
            user_dn += ',' + self._user_rdn
        user_dn += ',' + self._base_dn
        return user_dn

    def _createUserRecord(self, user):
        """
        Creates a record from user object that can be used for storing
        user into LDAP
        """
        # If users live in a relative dn, build it properly
        user_dns = None
        if self._user_rdn:
            user_dns = self._user_rdn.split('=')

        # Get form data. Data is unicoded so encode to utf-8 for ldap support.
        uid = unicodedata.normalize('NFKD', user.username).encode('utf-8', 'ignore')
        cn = unicodedata.normalize('NFKD', user.getDisplayName()).encode('utf-8', 'ignore')
        sn = unicodedata.normalize('NFKD', user.lastName).encode('utf-8', 'ignore')
        pw = unicodedata.normalize('NFKD', user.password).encode('utf-8', 'ignore')
        mail = unicodedata.normalize('NFKD', user.mail).encode('utf-8', 'ignore')

        # Create record having mandatory information
        # We are always creating inetOrgPerson because it can hold all necessary information
        record = [
            ('objectclass', self._object_classes),
            (self._uid, [uid]),
            ('cn', [cn]),
            ('sn', [sn]),
            ('userpassword', [pw]),
            ('mail', [mail])
        ]

        # These are optional fields
        if user.givenName:
            gn = unicodedata.normalize('NFKD', user.givenName).encode('utf-8', 'ignore')
            record.append(('gn', [gn]))
        if user.mobile:
            mobile = unicodedata.normalize('NFKD', user.mobile).encode('utf-8', 'ignore')
            record.append(('mobile', [mobile]))
        if user_dns:
            record.append((user_dns[0], [user_dns[1]]))
        return record

    def _debugRecord(self, record):
        """ Internal function for debugging purposes

            Writes record data into debug stream so that it's easy to see
            what kind of record we are trying to store
        """
        conf.log.debug('record = [')
        for key, value in record:
            conf.log.debug("('" + key + "'), [" + ', '.join(value) + "]")
        conf.log.debug(']')

    def updateUser(self, user):
        """
        Updates user data from service --> LDAP
        """
        # TODO: Implement
        raise NotImplementedError('LDAP user update is not implemented, yet.')

    def _search_user(self, username):
        """
        Search user from the LDAP directory

        .. NOTE:: Requires LDAP connection

        """
        # Create search filter
        filter = '(&(objectclass=*)({0}={1}))'.format(self._uid,
            ldap.filter.escape_filter_chars(username))

        # Search user from search domain, attributes = None means all attributes
        data = None
        try:
            data = self._connection.search_s(self._base_dn, ldap.SCOPE_SUBTREE, filter, None)
        except:
            conf.log.exception('Invalid LDAP search!')
            return None

        # Use ldaphelper.get_search_results to create nice results
        results = get_search_results(data)

        # If less than one results => no results
        # If more than one results => can't decide which is right
        if len(results) == 1:
            return results[0]
        else:
            return None

    def _search_users_in_group(self, groupname):
        """
        Search users in a group from the LDAP directory

        .. NOTE:: Requires LDAP connection

        """
        # Create search filter
        filter = '(%s=%s)' % (self._group_cn, ldap.filter.escape_filter_chars(groupname))
        # Search user from search domain, attributes = None means all attributes
        data = None
        try:
            data = self._connection.search_s(self._group_dn, ldap.SCOPE_SUBTREE, filter, None)
        except:
            conf.log.exception('Invalid LDAP search')
            return None

        # Use ldaphelper.get_search_results to create nice results
        return get_search_results(data)

    @ldapconnection
    def userExists(self, username, password=None):
        """
        Check that user exists. If password given, checks it too

        :param str username:
            Name of the user. Name is internally transformed into LDAP format
            using ``_search_user(username).get_dn()``
        :param str password:
            Optional password
        :returns: True if user exists in LDAP. Otherwise False.
        """
        userdata = self._search_user(username)

        if not userdata:
            return False

        # Get dn from userdata
        dn = userdata.get_dn()

        if not dn:
            return False

        # Password not given, so it's ok now
        if password is None:
            return True

        try:
            self._connection.simple_bind_s(dn, password)
        except Exception as e:
            conf.log.warning('User %s was not found: %s' % (username, e))
            return False

        return True

    def getGroups(self, username):
        """
        Get list of user's groups from LDAP service.

        :returns: List of LDAP groups user belongs in LDAP server
        """
        groups = self.__cache.get_user_ldap_groups(username)
        if groups is not None:
            return groups

        groups = []
        with self.ldapcontext():
            userdata = self._search_user(username)

            if userdata and userdata.has_attribute(conf.ldap_groups_attribute_name):
                groups = userdata.get_attr_values(conf.ldap_groups_attribute_name)
                conf.log.debug('Retrieved LDAP groups for user %s: %s' % (username, groups))

            # NOTE: Even if user does not have attribute or its empty, settle it for now.
            self.__cache.set_user_ldap_groups(username, groups)
        return groups

    def parseUsername(self, text):
        first_step = text.partition(',')
        if not first_step[1] == ',':
            return None

        second_step = first_step[0].partition('=')
        if not second_step[0] == 'employeeNumber' and not second_step[1] == '=':
            return None

        return second_step[2].lower()

    def getUsersInGroup(self, groupname):
        """
        Get list of usernames from specified LDAP group

        :param str groupname: Name of the LDAP group
        """
        usernames = self.__cache.get_ldap_group_users(groupname)
        if usernames is not None:
            return usernames

        usernames = []
        with self.ldapcontext():
            userdatas = self._search_users_in_group(groupname)
            if userdatas:
                for userdata in userdatas:
                    users = []
                    if userdata.has_attribute(conf.ldap_users_attribute_name):
                        users = userdata.get_attr_values(conf.ldap_users_attribute_name)

                    for user in users:
                        username = self.parseUsername(user)
                        if username:
                            usernames.append(username)

        if usernames:
            self.__cache.set_ldap_group_users(groupname, usernames)

        return usernames


def get_userstore():
    """
    Returns the active userstore.
    Currently only MySqlUserStore is supported

    >>> from multiproject.core.users import get_userstore
    >>> userstore = get_userstore()
    >>> userstore.getUser('username')

    :returns: User store
    :rval: MySqlUserStore
    """
    return MySqlUserStore()


def get_authstore():
    """
    Returns the active authentication store.
    Currently only LDAPAuthStore is supported

    >>> from multiproject.core.users import get_authstore
    >>> authstore = get_authstore()
    >>> authstore.userExists('username', 'password')

    :returns: Authentication store
    :rval: LdapUserStore
    """
    return LdapUserStore()
