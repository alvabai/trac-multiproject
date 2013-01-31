import unittest
import tags
import tagsadminpanel

def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(tags.TagsTestCase))
    testsuite.addTest(unittest.makeSuite(tagsadminpanel.TagsAdminPanelTestCase))
    return testsuite

if __name__ == '__main__':
    unittest.main(defaultTest = 'suite')
