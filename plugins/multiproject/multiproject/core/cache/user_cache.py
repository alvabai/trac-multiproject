from multiproject.core.configuration import conf
from multiproject.core.exceptions import SingletonExistsException
import base64

class UserCache(object):
    """ Methods for caching users
    """
    __instance = None

    def __init__(self):
        if UserCache.__instance:
            raise SingletonExistsException()
        self.mc = conf.getMemcachedInstance()
        self.USER_CACHE_TIME = 5 * 60

    @staticmethod
    def instance():
        if UserCache.__instance is None:
            UserCache.__instance = UserCache()
        return UserCache.__instance

    # Member count in projects
    def setTotalMemberCount(self, count):
        key = self.__members_in_projects_key()
        self.mc.set(key, count, self.USER_CACHE_TIME)

    def getTotalMemberCount(self):
        key = self.__members_in_projects_key()
        return self.mc.get(key)

    def clearTotalMemberCount(self):
        key = self.__members_in_projects_key()
        self.mc.delete(key)

    # Cookie value => username mapping
    def setUserCookieName(self, username, cookie_value):
        if cookie_value and username:
            key = self.__user_cookie_key(cookie_value)
            self.mc.set(key, username, self.USER_CACHE_TIME)

    def getUserCookieName(self, cookie_value):
        key = self.__user_cookie_key(cookie_value)
        return self.mc.get(key)

    def clearUserCookieName(self, cookie_value):
        key = self.__user_cookie_key(cookie_value)
        self.mc.delete(key)

    # User permission caching on a project
    def setUser(self, user):
        # Store user with both name and id
        self.mc.set(self.__user_key(user.username), user, self.USER_CACHE_TIME)
        self.mc.set(self.__user_key(user.id), user, self.USER_CACHE_TIME)

    def getUser(self, keysuffix):
        """
        Reads user from memcache, based on given keysuffix - which can be either username or user id
        :param mixed keysuffix: Either id or str or unicode
        """
        key = self.__user_key(keysuffix)
        return self.mc.get(key)

    def clearUser(self, keysuffix):
        """
        Clears user cache based on given key
        :param mixed keysuffix: Either id or str or unicode
        """
        key = self.__user_key(keysuffix)
        return self.mc.delete(key)

    # Key getters
    def __user_key(self, username):
        key = 'user:' + base64.b64encode(unicode(username))
        return key.encode('utf-8')

    def __members_in_projects_key(self):
        return 'total_members'.encode('utf-8')

    def __user_cookie_key(self, cookie_value):
        key = 'user_cookie:' + base64.b64encode(cookie_value)
        return key.encode('utf-8')
