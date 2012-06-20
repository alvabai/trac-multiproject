# -*- coding: utf-8 -*-
from multiproject.core.test.cqdetestcase import CQDETestCase
import multiproject.common.permissions
import trac.core
from multiproject.tests.ConfigurationStub import conf
from multiproject.core.permissions import CQDEPermissionStore
from multiproject.core.cache.project_cache import ProjectCache

class GlobalPermissionStoreTestCase(CQDETestCase):

    def setUp(self):
        conf.use_test_db(True)
        self.load_fixtures()
        self.cm = trac.core.ComponentManager()

    def tearDown(self):
        self.cm = None
        conf.use_test_db(False)

    # TODO
    #def test_get_user_permissions(self):
        #g = multiproject.common.permissions.GlobalPermissionStore(self.cm)
        #g.env = self; g.env.log = self
        #g._GlobalPermissionStore__store = CQDEPermissionStore(19)
        #self.assertEquals(g.get_user_permissions('cartman'), ['MODIFY', 'CREATE'])
        #self.assertEquals(g.get_user_permissions('kenny'), [])

    def test_get_users_with_permissions(self):
        g = multiproject.common.permissions.GlobalPermissionStore(self.cm)
        g.env = self; g.env.log = self
        g._GlobalPermissionStore__store = CQDEPermissionStore(19)
        self.assertEquals(g.get_users_with_permissions(['MODIFY', 'CREATE']), ['cartman'])
        self.assertEquals(g.get_users_with_permissions(['TRAC_ADMIN']), ['tracadmin'])

    def test_get_all_permissions(self):
        g = multiproject.common.permissions.GlobalPermissionStore(self.cm)
        g.env = self; g.env.log = self
        g._GlobalPermissionStore__store = CQDEPermissionStore(21)
        self.assertEquals(g.get_all_permissions(), [('cartman', 'VIEW'), ('tracadmin', 'TRAC_ADMIN')])

    def test_grant_permission(self):
        g = multiproject.common.permissions.GlobalPermissionStore(self.cm)
        g.env = self; g.env.log = self
        self.assertRaises(Exception, g.grant_permission, "user", "VIEW")

    def test_revoke_permission(self):
        g = multiproject.common.permissions.GlobalPermissionStore(self.cm)
        g.env = self; g.env.log = self
        self.assertRaises(Exception, g.revoke_permission, "user", "VIEW")

    # dummy log.debug
    def debug(self, msg):
        pass

    # dummy log.info
    def info(self, msg):
        pass

class GlobalPermissionPolicyTestCase(CQDETestCase):

    def setUp(self):
        self.cm = trac.core.ComponentManager()
        self.path = '/trac/storageauthtest'

    def tearDown(self):
        self.cm = None
        conf.use_test_db(False)

    def test_get_permission_actions(self):
        g = multiproject.common.permissions.GlobalPermissionPolicy(self.cm)
        actions = g.get_permission_actions()
        self.assertIn('VERSION_CONTROL', actions)
        self.assertIn('VIEW', actions)
        self.assertIn('MODIFY', actions)
        self.assertIn('CREATE', actions)
        self.assertIn('DELETE', actions)

    def test_check_permission(self):
        conf.use_test_db(True)
        self.load_fixtures()

        cache = ProjectCache.instance()
        cache.clearProjectId('storageauthtest')
        g = multiproject.common.permissions.GlobalPermissionPolicy(self.cm)
        g.env = self; g.env.log = self
        self.assertTrue(g.check_permission('VERSION_CONTROL_VIEW', 'kenny', None, None))
        self.assertTrue(g.check_permission('VERSION_CONTROL', 'kenny', None, None))
        self.assertFalse(g.check_permission('VERSION_CONTROL', 'cartman', None, None))

    def debug(self, msg):
        pass
