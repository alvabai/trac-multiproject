from multiproject.core.configuration import conf
import base64


class RssCache(object):
    """ Methods for caching RSS feeds (will cache the whole feed)
    """

    def __init__(self):
        # 5 minutes
        self.LIFETIME = 300
        self.mc = conf.getMemcachedInstance()

    def set_rss_feed(self, address, rss):
        key = self.create_key(address)
        return self.mc.set(key, rss, self.LIFETIME)

    def get_rss_feed(self, address):
        key = self.create_key(address)
        return self.mc.get(key)

    def create_key(self, suffix):
        key = 'rss_feed:' + base64.b64encode(suffix)
        return key
