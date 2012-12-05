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
