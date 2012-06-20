from multiproject.core.configuration import conf
from multiproject.core.exceptions import SingletonExistsException
import base64

class EventCache(object):
    """ Methods for caching events
    """
    __instance = None

    def __init__(self):
        if EventCache.__instance:
            raise SingletonExistsException()
        self.mc = conf.getMemcachedInstance()
        self.EVENT_CACHE_TIME = 60

    @staticmethod
    def instance():
        if EventCache.__instance is None:
            EventCache.__instance = EventCache()
        return EventCache.__instance

    def __set(self, key, file, timeout):
        self.mc.set(key, file, timeout)

    def webdav(self, username, project, file):
        key = "webdav.%s%s" % (base64.b64encode(username), base64.b64encode(project))
        last_event = self.mc.get(key)
        if last_event:
            self.mc.delete(key)
            return last_event
        else:
            self.__set(key, file, self.EVENT_CACHE_TIME)
            return None
