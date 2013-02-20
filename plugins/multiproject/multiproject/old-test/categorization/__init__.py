import unittest
import categorizationadminpanel

def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(categorizationadminpanel.CategorizationAdminPanelTestCase))
    return testsuite

if __name__ == '__main__':
    unittest.main(defaultTest = 'suite')
