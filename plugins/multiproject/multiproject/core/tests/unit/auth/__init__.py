import unittest
import basic_auth_test
import dav_access_test
import git_access_test
import hg_access_test

def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(basic_auth_test.BasicAccessTest))
    testsuite.addTest(unittest.makeSuite(dav_access_test.DavAccessControlTestCase))
    testsuite.addTest(unittest.makeSuite(git_access_test.GitAccessControlTestCase))
    testsuite.addTest(unittest.makeSuite(hg_access_test.HgAccessControlTestCase))
    return testsuite

if __name__ == '__main__':
    unittest.main(defaultTest = 'suite')
