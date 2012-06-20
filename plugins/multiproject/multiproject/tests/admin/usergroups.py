# -*- coding: utf-8 -*-
from multiproject.core.test.cqdetestcase import CQDETestCase
from multiproject.common.admin.usergroups import UserGroupsAdminPanel
import trac.core
from multiproject.tests.ConfigurationStub import conf
from multiproject.core.stubs import DummyEnv
from multiproject.core.stubs.RequestStub import DummyReq

class UserGroupsAdminPanelTestCase(CQDETestCase):

    def setUp(self):
        self.cm = trac.core.ComponentManager()
        conf.use_test_db(True)
        self.load_fixtures()

    def tearDown(self):
        self.cm = None
        conf.use_test_db(False)

    def test_add_and_remove_user_from_group(self):
        g = UserGroupsAdminPanel(self.cm)
        args = {'group':'my_test_group', 'add':1, 'user':'cartman'}
        req = DummyReq('tracadmin', 'q234twsnfjs', 'POST', '/test', args, ['PERMISSION_GRANT'])
        g.env = DummyEnv(req)

        page, args = g.render_admin_panel(req, None, None, None)
        self.assertEquals(page, 'admin_usergroups.html')
        self.assertIn('user_groups', args)
        self.assertIn('organization_groups', args)
        self.assertIn('organizations', args)
        self.assertIn('sorting', args)
        self.assertNotEquals(req.chrome['notices'], [])

        args = {'group':'my_test_group', 'remove':1, 'userremovelist':'cartman::scm_read'}
        req = DummyReq('tracadmin', 'q234twsnfjs', 'POST', '/test', args, ['PERMISSION_REVOKE'])
        g.env = DummyEnv(req)

        page, args = g.render_admin_panel(req, None, None, None)
        self.assertEquals(page, 'admin_usergroups.html')
        self.assertIn('user_groups', args)
        self.assertIn('organization_groups', args)
        self.assertIn('organizations', args)
        self.assertIn('sorting', args)
        self.assertNotEquals(req.chrome['notices'], [])

#    def test_add_and_remove_organization_from_group(self):
#        self.req.args['add_organization'] = 1
#        self.req.args['organizationgroup'] = self.testgroupname
#        self.req.args['organization'] = 'LDAP users'
#        
#        page, args = self.g.render_admin_panel(self.req, None, None, None)
#        self.assertEquals(page,'admin_usergroups.html')
#        self.assertIn('user_groups', args)
#        self.assertIn('organization_groups', args)
#        self.assertIn('organizations', args)
#        self.assertIn('sorting', args)
#        self.assertNotEquals(self.req.chrome['notices'], [])
#
#        self.req.args['add_organization'] = None
#        self.req.args['remove'] = 1
#        self.req.args['organizationremovelist'] = 'LDAP users::' + self.testgroupname
#
#        page, args = self.g.render_admin_panel(self.req, None, None, None)
#        self.assertEquals(page, 'admin_usergroups.html')
#        self.assertIn('user_groups', args)
#        self.assertIn('organization_groups', args)
#        self.assertIn('organizations', args)
#        self.assertIn('sorting', args)
#        self.assertNotEquals(self.req.chrome['notices'], [])
