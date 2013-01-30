import unittest2 as unittest

from common.projects.projectTest import *

class TestProjectModule(unittest.TestCase):
    def setUp(self):
        pass

    def test_create_project_with_name_as_project1_should_return_project1(self):
        project = ProjectStub(677, 677, "project1", "home project", 4, "2011-10-28-12:17:41", "home")
        self.assertEquals("project1", project.project_name)
        self.assertEquals(677, project.id)

    def test_create_project_with_name_as_project2_should_not_be_equal_with_project1(self):
        project = ProjectStub(678, 678, "project2", "home project", 4, "2011-10-28-12:17:41", "home")
        self.assertNotEqual("project1", project.project_name)
        self.assertEqual(678, project.id)