# -*- coding: utf-8 -*-
from multiproject.core.test.cqdetestcase import CQDETestCase
import multiproject.home.admin.plugins
import trac.core
from multiproject.tests.ConfigurationStub import dbStub


class DummyArgs(dict):
    def getlist(self, param):
        return self[param]


class DummyReq(object):
    def __init__(self):
        self.method = ''
        self.href = trac.web.Href('/tmp') #@UndefinedVariable
        self.args = DummyArgs()
        self.args['plugin'] = 1
        self.args['component'] = ['test', 'another']
        self.args['enable'] = ['test', 'another']
        self.args['prjenable'] = []
        self.args['setting'] = []
        self.args['static_setting'] = []

        class DummyPerm(object):
            def require(self, rights):
                pass

        self.perm = DummyPerm()

    def getlist(self, param):
        return []

    def redirect(self, uri):
        pass

class PluginAdminPanelTestCase(CQDETestCase):

    def setUp(self):
        self.cm = trac.core.ComponentManager()
        self.req = DummyReq()
        self.path = 'path' # dummy env.path
        self.save_called = False
        self.updateset = {}
        dbStub.addResult([[]])

    def tearDown(self):
        self.cm = None
        self.req = None
        dbStub.reset()

    def test_render_view(self):
        g = multiproject.home.admin.plugins.PluginAdminPanel(self.cm)
        g.env = self; g.config = self
        page, data = g.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_home_plugins.html')
        self.assertTrue(data.has_key('plugins'))
        self.assertTrue(data.has_key('readonly'))

    def test_do_update(self):
        self.req.method = 'POST'
        g = multiproject.home.admin.plugins.PluginAdminPanel(self.cm)
        g.env = self; g.config = self; g.log = self
        page, data = g.render_admin_panel(self.req, None, None, None) #@UnusedVariable
        self.assertEquals(page, 'admin_home_plugins.html')
        self.assertTrue(self.save_called)
        self.assertEquals(self.updateset['components'], ['test', 'enabled'])

    def test_is_component_enabled(self):
        self.config = self
        self.assertTrue(multiproject.home.admin.plugins.is_component_enabled(self, 'trac.some.component'))
        self.assertFalse(multiproject.home.admin.plugins.is_component_enabled(self, 'test'))
        self.assertFalse(multiproject.home.admin.plugins.is_component_enabled(self, 'webadmin.component'))

    # dummy config.options
    def options(self, section):
        return [
            ['webadmin.*', 'enabled'],
            ['test', 'disabled'],
            ['another', 'enabled'],
            ['multiproject.tags.*', 'required'],
            ['multiproject.admin.plugins.*', 'enabled']
        ]
    # dummy config.get
    def get(self, section, option):
        return None
    # dummy config.set
    def set(self, categ, component, onoff):
        self.updateset[categ] = [component, onoff]
    # dummy config.save
    def save(self):
        self.save_called = True
    # dummy log.info
    def info(self, *args):
        pass
