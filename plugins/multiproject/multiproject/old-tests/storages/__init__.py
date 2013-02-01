import unittest
import storagesadminpanel

def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(storagesadminpanel.StoragesAdminPanelTestCase))
    return testsuite

if __name__ == '__main__':
    unittest.main(defaultTest = 'suite')
