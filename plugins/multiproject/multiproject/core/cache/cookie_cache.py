from multiproject.core.configuration import conf
from multiproject.core.multiproj_exceptions import SingletonExistsException
import base64

class CookieCache(object):
    """ Methods for cache cookie expire times 
    """
    __instance = None

    def __init__(self):
        if CookieCache.__instance:
            raise SingletonExistsException()
        self.mc = conf.getMemcachedInstance()

    @staticmethod
    def instance():
        if CookieCache.__instance is None:
            CookieCache.__instance = CookieCache()
        return CookieCache.__instance

    def add(self, cookie):
        if cookie:
            key = self.__cookie_key(cookie)
            self.mc.set(key, '1', conf.cookie_refresh_rate)

    def remove(self, cookie):
        key = self.__cookie_key(cookie)
        self.mc.delete(key)
        pass

    def get(self, cookie):
        key = self.__cookie_key(cookie)
        return self.mc.get(key)

    def __cookie_key(self, cookie_value):
        key = 'active-item-' + base64.b64encode(cookie_value)
        return key.encode('utf-8')

