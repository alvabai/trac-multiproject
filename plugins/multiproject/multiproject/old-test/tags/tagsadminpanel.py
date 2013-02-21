# -*- coding: utf-8 -*-
from multiproject.core.test.cqdetestcase import CQDETestCase
from multiproject.core.cache.project_cache import ProjectCache

from multiproject.project.admin.tags import TagsAdminPanel
from multiproject.tests.ConfigurationStub import dbStub
from multiproject.common.tags import Tags

import trac.core
from trac.web import Href


class DummyReq(object):
    def __init__(self):
        self.args = {
            'action': '',
            'tag': 'test tag'
        }

        class DummyPerm(object):
            def require(self, rights):
                pass

        self.perm = DummyPerm()
        self.method = 'POST'
        self.base_path = 'path'
        self.href = Href('/tmp') #@UndefinedVariable
        self.chrome = {}

class TagsAdminPanelTestCase(CQDETestCase):

    def setUp(self):
        dbStub.addResult([[1]])
        dbStub.addResult([])
        self.cm = trac.core.ComponentManager()
        self.req = DummyReq()
        self.path = '/trac/tmp' # dummy env.path
        self.add_called = False
        self.remove_called = False
        self.orig_add = Tags.add #@UndefinedVariable
        self.orig_remove = Tags.remove #@UndefinedVariable
        Tags.add = self.add
        Tags.remove = self.remove
        cache = ProjectCache.instance()
        cache.clearProjectId("tmp")
        cache.clearProject("tmp")
        
    def tearDown(self):
        dbStub.reset()
        self.cm = None
        self.req = None
        Tags.add = self.orig_add
        Tags.remove = self.orig_remove

    def test_render_admin_panel_add(self):
        self.req.args['action'] = 'Add'
        t = TagsAdminPanel(self.cm)
        t.env = self
        page, data = t.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'tags.html')
        self.assertTrue(data.has_key('cloud'))
        self.assertTrue(data.has_key('prj_tags'))
        self.assertTrue(self.add_called)
        self.assertTrue(dbStub.closed)

    def test_render_admin_panel_remove(self):
        self.req.args['action'] = 'Remove'
        t = TagsAdminPanel(self.cm)
        t.env = self
        page, data = t.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'tags.html')
        self.assertTrue(data.has_key('cloud'))
        self.assertTrue(data.has_key('prj_tags'))
        self.assertTrue(self.remove_called)
        self.assertTrue(dbStub.closed)

    # dummy Tags.add
    def add(self, project, tag):
        self.add_called = True

    # dummy Tags.remove
    def remove(self, project, tag):
        self.remove_called = True
