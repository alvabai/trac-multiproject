import unittest
import admin
import admin_editusers
import auth
import icon
import login
import preferences

def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(admin.CreateUserAdminPanelTestCase))
    testsuite.addTest(unittest.makeSuite(admin.RemoveUsersTestCase))
    testsuite.addTest(unittest.makeSuite(admin_editusers.EditUsersTestCase))
    testsuite.addTest(unittest.makeSuite(auth.AuthenticationTestCase))
    testsuite.addTest(unittest.makeSuite(icon.IconRendererTestCase))
    testsuite.addTest(unittest.makeSuite(login.GlobalLoginModuleTestCase))
    testsuite.addTest(unittest.makeSuite(preferences.UserBasicInfoTestCase))
    testsuite.addTest(unittest.makeSuite(preferences.UserImagePreferencePanelTestCase))
    testsuite.addTest(unittest.makeSuite(preferences.UserChangePasswordTestCase))
    return testsuite

if __name__ == '__main__':
    unittest.main(defaultTest = 'suite')
