import unittest
import api
import commands

def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(api.ProjectsApiTestCase))
    testsuite.addTest(unittest.makeSuite(api.ProjectTestCase))
    testsuite.addTest(unittest.makeSuite(commands.CommanderTestCase))
    testsuite.addTest(unittest.makeSuite(commands.CreateTracDatabaseTestCase))
    testsuite.addTest(unittest.makeSuite(commands.ListUpProjectTestCase))
    testsuite.addTest(unittest.makeSuite(commands.SetPermissionsTestCase))
    return testsuite

if __name__ == '__main__':
    unittest.main(defaultTest = 'suite')
