# -*- coding: utf-8 -*-
import unittest2 as unittest
from core.regMock import *
from common.projects.projectsTest import *
from common.projects.projectTest import *
from common.featured.adminTest import *

class TestFeaturedAdminPanel(unittest.TestCase):
    def setUp(self):
        pass

    def test_render_admin_panel_with_searchprojects(self):
        req = ReqMock("POST")
        req.args.setGetParam("searchprojects")
        admin_panel = FeaturedProjectsAdminPanel()
        projects_data = admin_panel.render_admin_panel(req)
        self.assertIsNotNone(projects_data['selected'])
        self.assertTrue(isinstance(projects_data['selected'], list))
        self.assertTrue(len(projects_data['selected']) == 2)
        self.assertEqual(1, projects_data['selected'][0].id)
        self.assertEqual(2, projects_data['selected'][1].id)

    def test_render_admin_panel_with_update(self):
        req = ReqMock("POST")
        req.args.setGetParam("update")
        admin_panel = FeaturedProjectsAdminPanel()
        projects_data = admin_panel.render_admin_panel(req)
        self.assertIsNotNone(projects_data['selected'])
        self.assertTrue(isinstance(projects_data['selected'], list))
        self.assertTrue(len(projects_data['selected']) == 3)
        self.assertEqual(3, projects_data['selected'][0][0][0])
        self.assertEqual(4, projects_data['selected'][1][0][0])
        self.assertEqual(5, projects_data['selected'][2][0][0])

