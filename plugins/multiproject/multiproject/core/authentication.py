from multiproject.core.cache import GroupPermissionCache
from multiproject.core.configuration import conf
from multiproject.core.db import admin_query, safe_int, admin_transaction
from multiproject.core.exceptions import SingletonExistsException


class CQDEAuthenticationStore(object):
    """ DAO for authentications
    """
    _instance = None

    def __init__(self):
        if CQDEAuthenticationStore._instance:
            raise SingletonExistsException("Use CQDEAuthenticationStore.instance()")
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
