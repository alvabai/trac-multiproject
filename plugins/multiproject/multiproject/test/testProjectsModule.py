# -*- coding: utf-8 -*-
import unittest2 as unittest

from common.projects.projectsTest import *
from common.projects.projectTest import *

class TestProjectsModule(unittest.TestCase):
    def setUp(self):
        pass

    def test_with_proper_sql_to_get_two_projects(self):
        projects_group = ProjectsStub()
        projects = projects_group.get_featured_projects()
        self.assertEqual("Project1", projects[0].project_name)
        self.assertEqual("Home", projects[1].project_name)

    def test_with_count_to_get_different_projects(self):
        projects_group = ProjectsStub()
        projects = projects_group.get_featured_projects(4)
        self.assertNotEqual("Project1", projects[0].project_name)
        self.assertNotEqual("Home", projects[1].project_name)
        self.assertEqual("Project3", projects[0].project_name)
        self.assertEqual("Project5", projects[1].project_name)

    def test_search_projects_with_keyword_project_should_return_dictionary(self):
        projects_group = ProjectsStub()
        project = projects_group.search_project("project", 1)
        self.assertEqual(1, project["project_id"])