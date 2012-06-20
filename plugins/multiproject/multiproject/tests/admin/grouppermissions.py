# -*- coding: utf-8 -*-
import trac.core
import trac.web

import multiproject.common.admin.grouppermissions
from multiproject.tests.ConfigurationStub import conf
from multiproject.core.permissions import CQDEUserGroupStore
from multiproject.core.test.cqdetestcase import CQDETestCase

class DummyArgs(dict):
    def getlist(self, param):
        return self[param]


class DummyReq(object):
    def __init__(self):
        self.method = 'POST'
        self.href = trac.web.Href('/tmp') #@UndefinedVariable
        self.args = DummyArgs()
        self.args['group'] = None
        self.chrome = DummyArgs()
        self.chrome['warnings'] = []
        self.chrome['notices'] = []

        class DummyPerm(object):
            def require(self, rights):
                pass

        self.perm = DummyPerm()

class GroupPermissionAdminPanelTestCase(CQDETestCase):

    def setUp(self):
        conf.memcached_enabled = False
        self.cm = trac.core.ComponentManager()
        self.req = DummyReq()
        self.path = "/test"
        self.testgroupname = 'my_test_group'
        conf.use_test_db(True)
        self.load_fixtures()
        self.g = multiproject.common.admin.grouppermissions.GroupPermissionAdminPanel(self.cm)
        self.g.env = self; self.g.env.log = self
        self.g._get_project_id = self._get_project_id
        self.g._get_all_permissions = self._get_all_permissions

    def tearDown(self):
        self.cm = None
        self.req = None
        self._clear_db()
        conf.use_test_db(False)
        conf.memcached_enabled = True

    def _clear_db(self):
        store = CQDEUserGroupStore(self._get_project_id())
        store.remove_group(self.testgroupname)

    def test_add_and_remove_permission_from_group(self):
        self.req.args['add'] = 1
        self.req.args['group'] = self.testgroupname
        self.req.args['permission'] = 'VIEW'

        page, args = self.g.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_grouppermissions.html')
        self.assertIn('available_permissions', args)
        self.assertEquals(args['available_permissions'], self._get_all_permissions())
        self.assertIn('group_permissions', args)
        self.assertIn('templates', args)
        self.assertNotEquals(self.req.chrome['notices'], [])

        self.req.args['add'] = None
        self.req.args['remove'] = 1
        self.req.args['permremovelist'] = self.testgroupname + '::VIEW'

        page, args = self.g.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_grouppermissions.html')
        self.assertIn('available_permissions', args)
        self.assertEquals(args['available_permissions'], self._get_all_permissions())
        self.assertIn('group_permissions', args)
        self.assertIn('templates', args)
        self.assertNotEquals(self.req.chrome['notices'], [])

    def test_remove_groups(self):
        store = CQDEUserGroupStore(self._get_project_id())
        store.create_group(self.testgroupname)

        self.req.args['remove'] = 1
        self.req.args['groupremovelist'] = self.testgroupname

        page, args = self.g.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_grouppermissions.html')
        self.assertIn('available_permissions', args)
        self.assertEquals(args['available_permissions'], self._get_all_permissions())
        self.assertIn('group_permissions', args)
        self.assertIn('templates', args)
        self.assertNotEquals(self.req.chrome['notices'], [])

    # dummy methods
    def _get_project_id(self):
        return 19

    def _get_all_permissions(self):
        return ['TRAC_ADMIN', 'VIEW', 'CREATE']
