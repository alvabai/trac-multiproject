import unittest
from unit import permission_cache_test, user_cache_test, project_cache_test,\
    users_test, cqdecategorystore_test, cqdewatchliststore_test, ssh_keys_test, auth

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(permission_cache_test.PermissionCacheTestCase))
    suite.addTest(unittest.makeSuite(permission_cache_test.AuthenticationCacheTestCase))
    suite.addTest(unittest.makeSuite(user_cache_test.UserCacheTestCase))
    suite.addTest(unittest.makeSuite(project_cache_test.ProjectCacheTestCase))
    suite.addTest(auth.suite())
    suite.addTest(unittest.makeSuite(users_test.UserTestCase))
    suite.addTest(unittest.makeSuite(users_test.MySqlUserStoreTestCase))
    suite.addTest(unittest.makeSuite(users_test.LdapUserStoreTestCase))
    suite.addTest(unittest.makeSuite(cqdecategorystore_test.CQDECategoryStoreTestCase))
    suite.addTest(unittest.makeSuite(cqdewatchliststore_test.CQDEWatchlistStoreTestCase))
    suite.addTest(unittest.makeSuite(ssh_keys_test.SshKeysTestCase))
    suite.addTest(unittest.makeSuite(ssh_keys_test.CQDESshKeyStoreTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest = 'suite')
