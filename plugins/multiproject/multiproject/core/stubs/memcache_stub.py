class MemcacheStub(object):
    """ Class that can be used when memcached is disabled
        in the configuration.
    """

    def get(self, key):
        return None

    def set(self, key, value, inv_time=None):
        pass

    def delete(self, key):
        pass
