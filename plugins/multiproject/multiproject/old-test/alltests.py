# -*- coding: utf-8 -*-
import unittest
import admin, categorization, frontpage, projectlist, projects, users
import basicsadminpanel
import permissions
import xmlrpc

def suite():
    suite = unittest.TestSuite()
    suite.addTest(admin.suite())
    suite.addTest(categorization.suite())
    suite.addTest(frontpage.suite())
    suite.addTest(projectlist.suite())
    suite.addTest(projects.suite())
    suite.addTest(users.suite())
    suite.addTest(unittest.makeSuite(basicsadminpanel.BasicsAdminPanelInterceptorTestCase))
    suite.addTest(unittest.makeSuite(permissions.GlobalPermissionPolicyTestCase))
    suite.addTest(unittest.makeSuite(permissions.GlobalPermissionStoreTestCase))
    suite.addTest(unittest.makeSuite(xmlrpc.ProjectsRPCTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest = 'suite')
