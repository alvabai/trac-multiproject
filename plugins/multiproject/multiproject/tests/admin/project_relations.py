# -*- coding: utf-8 -*-
import trac.core

import multiproject
from multiproject.core.test.cqdetestcase import CQDETestCase
from multiproject.core.stubs.RequestStub import DummyReq
from multiproject.core.stubs.DummyEnv import DummyEnv
from multiproject.tests.ConfigurationStub import conf

class ProjectRelationsAdminPanelTestCase(CQDETestCase):
    def setUp(self):
        self.cm = trac.core.ComponentManager()

    def tearDown(self):
        self.cm = None
        conf.use_test_db(False)

    def test_request_when_have_childs(self):
        view = multiproject.project.admin.projectrelations.ProjectForkingAdminPanel(self.cm)
        conf.use_test_db(True)
        self.load_fixtures()

        req = DummyReq("username", "password", "GET", "/trac/publicroject", {})
        req.permissions = ['TRAC_ADMIN']
        view.env = DummyEnv(req)
        page, data = view.render_admin_panel(req, None, None, None)

        self.assertEquals(page, 'admin_relations_panel.html')
        self.assertIn('_project_', data)
        self.assertIn('parent_project', data)
        self.assertIn('child_projects', data)
        self.assertIn('home', data)
        self.assertEquals(len(data['child_projects']), 1)
        self.assertEquals(data['parent_project'], None)

    def test_request_when_have_parent(self):
        view = multiproject.project.admin.projectrelations.ProjectForkingAdminPanel(self.cm)
        conf.use_test_db(True)
        self.load_fixtures()

        req = DummyReq("username", "password", "GET", "/trac/cartoons", {})
        req.permissions = ['TRAC_ADMIN']
        view.env = DummyEnv(req)
        page, data = view.render_admin_panel(req, None, None, None)

        self.assertEquals(page, 'admin_relations_panel.html')
        self.assertIn('_project_', data)
        self.assertIn('parent_project', data)
        self.assertIn('child_projects', data)
        self.assertIn('home', data)
        self.assertEquals(len(data['child_projects']), 0)
        self.assertEquals(data['parent_project'].env_name, 'publicroject')
