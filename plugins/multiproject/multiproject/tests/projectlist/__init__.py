import unittest
import projectlist

def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(projectlist.ProjectListTestCase))
    return testsuite

if __name__ == '__main__':
    unittest.main(defaultTest = 'suite')
