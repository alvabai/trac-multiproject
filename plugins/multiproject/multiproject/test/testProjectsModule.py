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

    def test_search_projects_with_keyword_project_should_return_list(self):
        projects_group = ProjectsStub()
        projects = projects_group.search_project("project", 1)
        i = 1
        for project in projects:
            self.assertEqual(i, project.id)
            i += 1

    def test_update_feature_projects_with_project_list_should_return_true(self):
        projects_group = ProjectsStub()
        project_data = [[3,
                         "Project3",
                         None,
                         None,
                         "4",
                         None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         "12"],
                        [4,
                         "Project4",
                         None,
                         None,
                         "4",
                         None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         "15"],
                        [5,
                         "Project5",
                         None,
                         None,
                         "4",
                         None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         "12"]
        ]
        self.assertTrue(projects_group.update_featured_projects(project_data))

    def test_update_featured_projects_without_list_should_return_false(self):
        projects_group = ProjectsStub()
        self.assertFalse(projects_group.update_featured_projects(None))