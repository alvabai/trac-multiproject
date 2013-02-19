import unittest
import welcome

def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(welcome.WelcomeModuleTestCase))
    return testsuite

if __name__ == '__main__':
    unittest.main(defaultTest = 'suite')
