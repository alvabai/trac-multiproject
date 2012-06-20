import unittest
import plugins
import grouppermissions
import grouptemplates
import usergroups
import project_relations

def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(plugins.PluginAdminPanelTestCase))
    testsuite.addTest(unittest.makeSuite(grouppermissions.GroupPermissionAdminPanelTestCase))
    testsuite.addTest(unittest.makeSuite(usergroups.UserGroupsAdminPanelTestCase))
    testsuite.addTest(unittest.makeSuite(project_relations.ProjectRelationsAdminPanelTestCase))
    return testsuite

if __name__ == '__main__':
    unittest.main(defaultTest = 'suite')
