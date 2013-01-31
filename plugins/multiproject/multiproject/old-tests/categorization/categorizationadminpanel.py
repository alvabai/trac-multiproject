# -*- coding: utf-8 -*-
from multiproject.core.categories import CQDECategoryStore
import multiproject.project.admin.categories
import trac.core
from multiproject.tests.ConfigurationStub import dbStub
from multiproject.core.test.cqdetestcase import CQDETestCase

class DummyReq(object):
    def __init__(self):
        self.args = {
            'action': '',
            'context_key': 2
        }

        class DummyPerm(object):
            def require(self, rights):
                pass

        self.perm = DummyPerm()
        self.method = 'POST'
        self.base_path = '/cartoon'
        self.href = trac.web.Href('/cartoon') #@UndefinedVariable
        self.chrome = {}

def dummy_get_project_categories():
    return None

class CategorizationAdminPanelTestCase(CQDETestCase):

    def setUp(self):
        dbStub.addResult([[1]])
        dbStub.addResult([])
        self.cm = trac.core.ComponentManager()
        self.req = DummyReq()
        self.path = 'path' # dummy env.path
        self.project_name = "path"
        self.bind_called = False
        self.unbind_called = False
        self.orig_bind = CQDECategoryStore().bind_category_project #@UndefinedVariable
        self.orig_unbind = CQDECategoryStore().unbind_category_project #@UndefinedVariable
        CQDECategoryStore().bind_category_project = self.bind
        CQDECategoryStore().unbind_category_project = self.unbind

    def tearDown(self):
        dbStub.reset()
        self.cm = None
        self.req = None
        CQDECategoryStore().bind_category_project = self.orig_bind
        CQDECategoryStore().unbind_category_project = self.orig_unbind

    def test_process_request_bind(self):
        self.req.args['action'] = 'bind'
        c = multiproject.project.admin.categories.CategorizationAdminPanel(self.cm)
        c._get_project_categories = dummy_get_project_categories
        c.first_context = 1
        c.env = self
        page, data, tmp = c.process_request(self.req) #@UnusedVariable
        self.assertEquals(page, 'categories.html')
        self.assertEquals(data['context_key'], 2)
        self.assertTrue(self.bind_called)
        self.assertTrue(dbStub.closed)

    def test_process_request_unbind(self):
        self.req.args['action'] = 'unbind'
        c = multiproject.project.admin.categories.CategorizationAdminPanel(self.cm)
        c._get_project_categories = dummy_get_project_categories
        c.first_context = 1
        c.env = self
        page, data, tmp = c.process_request(self.req) #@UnusedVariable
        self.assertEquals(page, 'categories.html')
        self.assertEquals(data['context_key'], 2)
        self.assertTrue(self.unbind_called)
        self.assertTrue(dbStub.closed)

    def test_render_admin_panel(self):
        c = multiproject.project.admin.categories.CategorizationAdminPanel(self.cm)
        c.env = self
        page, data = c.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_categories.html')
        self.assertEquals(data['env'], '/cartoon')
        self.assertTrue(data.has_key('contexts'))
        self.assertTrue(dbStub.closed)

    # dummy CQDECategoryStore.bind_category_project
    def bind(self, project, category):
        self.bind_called = True

    # dummy CQDECategoryStore.unbind_category_project
    def unbind(self, project, category):
        self.unbind_called = True


