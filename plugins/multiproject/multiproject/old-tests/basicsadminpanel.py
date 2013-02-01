# -*- coding: utf-8 -*-
from multiproject.core.test.cqdetestcase import CQDETestCase
import multiproject
import trac.core

from multiproject.tests.ConfigurationStub import dbStub
from multiproject.core.cache.project_cache import ProjectCache

class DummyReq(object):
    def __init__(self):
        self.args = {
            'name': 'projname'
        }

        class DummyPerm(object):
            def require(self, rights):
                pass

        self.perm = DummyPerm()
        self.method = 'POST'

# dummy BasicsAdminPanel.render_admin_panel
def render(self, req, cat, page, path_info):
    return ''

class BasicsAdminPanelInterceptorTestCase(CQDETestCase):

    def setUp(self):
        dbStub.addResult([[1]]) # project id
        dbStub.addResult([])
        self.cm = trac.core.ComponentManager()
        self.req = DummyReq()
        self.path = 'path' # dummy env.path
        self.project_name = "path"
        self.project_description = "description"
        trac.admin.web_ui.BasicsAdminPanel.render_admin_panel = render
        cache = ProjectCache.instance()
        cache.clearProjectId("path")
        cache.clearProject("path")
        
    def tearDown(self):
        dbStub.reset()
        self.cm = None
        self.req = None

    def test_update_project_info(self):
        t = multiproject.project.admin.BasicsAdminPanelInterceptor(self.cm)
        t.update_project_info(1, 'name', 'url', 'description')
        self.assertTrue(dbStub.cursors[0].query.lower().startswith("update projects set project_name = 'name'"))
        self.assertTrue(dbStub.cursors[0].query.lower().endswith("where project_id = 1"))
        self.assertTrue(dbStub.closed)
