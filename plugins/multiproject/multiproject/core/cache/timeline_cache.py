from multiproject.core.configuration import Configuration
conf = Configuration.instance()


class TimelineCache(object):
    """ Methods for caching timeline (will cache the whole
        result set for pages)
    """

    def __init__(self):
        self.TIMELINE_CACHE_TIME = 3600 * 24 * 7
        self.mc = conf.getMemcachedInstance()

    # The whole global timeline page
    def get_global_timeline(self, username, rss=False):
        key = self.global_tl_key(username, rss)
        return self.mc.get(key)

    def set_global_timeline(self, username, data, rss=False):
        key = self.global_tl_key(username, rss)
        self.mc.set(key, data, self.TIMELINE_CACHE_TIME)

    def clear(self):
        # Clear all timeline cache at once
        self.mc.delete('globalGLTLRSSauth')
        self.mc.delete('globalGLTLRSSanon')
        self.mc.delete('globalGLTLauth')
        self.mc.delete('globalGLTLanon')

    def global_tl_key(self, username, rss):
        key = (rss and 'globalGLTLRSS') or 'globalGLTL'
        return key + self.anon_or_auth(username)

    def anon_or_auth(self, username):
        return (username == 'anonymous' and 'anon') or 'auth'
