# -*- coding: utf-8 -*-

import unittest2 as unittest

from core.regMock import *

class TestRegModule(unittest.TestCase):
    def setUp(self):
        pass

    def test_with_method_post_should_be_post(self):
        req = ReqMock("POST")
        self.assertEqual("POST", req.method)

    def test_permission_trac_admin_should_return_true(self):
        req = ReqMock("POST")
        self.assertTrue(req.perm.require("TRAC_ADMIN"))

    def test_permission_without_trac_admin_should_return_false(self):
        req = ReqMock("POST")
        self.assertFalse(req.perm.require("AUTHENTICATED"))

    def test_arguments_with_search_projects_should_return_true(self):
        req = ReqMock("POST")
        req.args.setGetParam("searchprojects")
        self.assertTrue(req.args.get("searchprojects"))

    def test_arguments_with_pattern_should_return_project(self):
        req = ReqMock("POST")
        req.args.setGetParam("searchprojects")
        self.assertEqual("project",req.args.get("pattern"))

    def test_arguments_with_update_should_return_true(self):
        req = ReqMock("POST")
        req.args.setGetParam("update")
        self.assertTrue(req.args.get("update"))

    def test_arguments_with_projects_should_return_list(self):
        req = ReqMock("POST")
        req.args.setGetParam("update")
        projects = req.args.get("projects")
        self.assertEqual(3, projects[0][0])
        self.assertEqual("Project3", projects[0][1])
        self.assertEqual(4, projects[1][0])
        self.assertEqual("Project4", projects[1][1])

    def test_arguments_with_list_should_return_1(self):
        req = ReqMock("POST")
        projects = req.args.get([1,2])
        self.assertEqual("1", projects)