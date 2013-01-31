# -*- coding: utf-8 -*-
import trac.core

import multiproject.project.admin.storages
from multiproject.tests.ConfigurationStub import conf
from multiproject.core.test.cqdetestcase import CQDETestCase


class DummyReq(object):
    def __init__(self):
        self.args = {
            'action': '',
            }

        class DummyPerm(object):
            def require(self, rights):
                pass

        self.perm = DummyPerm()
        self.method = 'POST'
        self.base_path = 'path'
        self.href = trac.web.Href('/tmp') #@UndefinedVariable
        self.chrome = {}

    def setmethod(self, method):
        self.method = method

    def setarg(self, arg, value):
        self.args[arg] = value


class StoragesAdminPanelTestCase(CQDETestCase):

    def setUp(self):
        conf.use_test_db(True)
        self.cm = trac.core.ComponentManager()
        self.req = DummyReq()
        self.path = '/path/test'
        self.add_called = False
        self.remove_called = False

    def tearDown(self):
        conf.use_test_db(False)
        self.cm = None
        self.req = None

    def test_render_admin_panel(self):
        panel = multiproject.project.admin.storages.StoragesAdminPanel(self.cm)
        panel.env = self; panel.config = self; panel.log = self
        page, data = panel.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'storages.html')
        self.assertNotEquals(data['vcs_url'], None)

    def test_get_templates_dirs(self):
        panel = multiproject.project.admin.storages.StoragesAdminPanel(self.cm)
        panel.env = self; panel.config = self; panel.log = self
        retval = panel.get_templates_dirs()
        self.assertNotEquals(retval, None)
