# coding=utf-8
from multiproject.core.cache.user_cache import UserCache
from multiproject.core.users import User
from multiproject.core.test.cqdetestcase import CQDETestCase

class UserCacheTestCase(CQDETestCase):
    def setUp(self):
        self._user1 = User()
        self._user1.id = 1
        self._user1.username = 'tester'
        self._user1.givenName = 'First'
        self._user1.lastName = 'Last'
        self._user1.mail = ''
        self._user1.mobile = ''
        self._user1.password = 'password'

        self._user2 = User()
        self._user2.id = 2
        self._user2.username = "scändic"
        self._user2.givenName = "Ääkkönen"
        self._user2.lastName = "Nimessä"
        self._user2.mail = ''
        self._user2.mobile = ''
        self._user2.password = 'password'
    
    def tearDown(self):
        pass
    
    def testSettingUser(self):
        cache = UserCache.instance()
        
        # First clear cache for test user
        cache.clearUser(self._user1.username)
        cache.clearUser(self._user2.username)
        
        cache.setUser(self._user1)
        cache.setUser(self._user2)
        
        # Test that simple user can be set and get correctly
        self.assertTrue(self._user1.equals(cache.getUser(self._user1.username)))
        cache.clearUser(self._user1.username)
        self.assertFalse(self._user1.equals(cache.getUser(self._user1.username)))
        cache.clearUser(self._user1.username)
        
        # Test that user having scandinavic name can be set and get correctly
        self.assertTrue(self._user2.equals(cache.getUser(self._user2.username)))
        cache.clearUser(self._user2.username)
        self.assertFalse(self._user2.equals(cache.getUser(self._user2.username)))
        cache.clearUser(self._user2.username)
