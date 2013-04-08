import unittest
import plugins
import grouptemplates

def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(plugins.PluginAdminPanelTestCase))
    return testsuite

if __name__ == '__main__':
    unittest.main(defaultTest = 'suite')
