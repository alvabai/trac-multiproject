# -*- coding: utf-8 -*-
from multiproject.common.projects import Projects, Project
from multiproject.core.test.cqdetestcase import CQDETestCase
from multiproject.tests.ConfigurationStub import conf, dbStub, userstoreStub
from multiproject.core.multiproj_exceptions import ProjectValidationException

project_tasks_result = [
    # url, summary, description, priority, time, priority_sort
    ["prj", "summary", "descr", "1", 9999, 1],
    ["prj", "summary", "descr", "2", 9999, 1],
    ["prj", "summary", "descr", "3", 9999, 1]
]

project_search_result = [
    [1, "Project 1", "project1", "descr1", 10, "2009-01-01", "2009-01-01", "2009-01-01", None, None, 1 ],
    [2, "Project 2", "project2", "descr2", 11, "2009-01-02", "2009-01-01", "2009-01-01", None, None, 2 ],
    [3, "Project 3", "project3", "descr3", 12, "2009-01-03", "2009-01-01", "2009-01-01", None, None, 3 ]
]

class ProjectsApiTestCase(CQDETestCase):

    def setUp(self):
        pass

    def tearDown(self):
        dbStub.reset()
        userstoreStub.reset()
        conf.use_test_db(False)

    def test_project_count(self):
        dbStub.addResult([ [3] ])
        p = Projects()
        self.assertEquals(p.project_count(), 3)
        self.assertTrue(dbStub.closed)

    def test_project_environment_exists(self):
        dbStub.addResult([ [1] ])
        p = Projects()
        self.assertTrue(p.project_environment_exists("testi"))
        self.assertTrue(dbStub.closed)

    def test_project_environment_does_not_exist(self):
        dbStub.addResult([ [0] ])
        p = Projects()
        self.assertFalse(p.project_environment_exists("testi"))
        self.assertTrue(dbStub.closed)

        dbStub.setExceptions(True)
        self.assertFalse(p.project_environment_exists("testi"))
        self.assertTrue(dbStub.closed)

    def test_get_my_tasks(self):
        dbStub.addResult(project_tasks_result)
        p = Projects()
        project_list = [
            Project(1, "project1", "project1", "Project 1", 1, "2010-01-01"),
            Project(2, "project2", "project2", "Project 2", 2, "2010-01-02")
        ]
        tasks = p.get_all_user_tasks("username", project_list)
        self.assertEquals(len(tasks), 6)
        self.assertTrue(dbStub.closed)

    def test_get_services(self):
        p = Projects()
        res={}
        p.getServices(res,"test, dummy, Subversion, Perforce, test")
        self.assertEquals(res['vcs_type'], "perforce")

        p.getServices(res,"test, dummy, Subversion, test")
        self.assertEquals(res['vcs_type'], "svn")

        p.getServices(res,"another test, Versioncontrol|Mercurial, test")
        self.assertEquals(res['vcs_type'], "hg")

        p.getServices(res," versioncontrol|git ")
        self.assertEquals(res['vcs_type'], "git")

        res['vcs_type']=None
        p.getServices(res,"test, test")
        self.assertEquals(res['vcs_type'], None)

        res['vcs_type']=None
        p.getServices(res,"")
        self.assertEquals(res['vcs_type'], None)

        p.getServices(res," versioncontrol|svn,versioncontrol|something")
        self.assertEquals(res['vcs_type'], "svn")

        res['vcs_type']=None

    def test_search_user_projects(self):
        dbStub.addResult(project_search_result)
        p = Projects()
        userstoreStub.user.username = "user"
        projects = p.searchUserProjects("name1 name2 name3","user")
        self.assertEquals(len(projects), 3)
        self.assertEquals(projects[0].env_name, 'project1')
        self.assertEquals(projects[0].project_name, 'Project 1')
        self.assertEquals(projects[0].author_id, 10)
        self.assertEquals(projects[0].created, '2009-01-01')
        self.assertTrue(dbStub.closed)

    def test_is_project_owner(self):
        dbStub.addResult([ [1] ]) # user id
        userstoreStub.user.id = 1
        p = Projects()
        self.assertTrue(p.is_project_owner("project", "user"))
        self.assertTrue(dbStub.closed)

    def test_is_project_owner_error(self):
        dbStub.addResult([ [1] ]) # user id
        userstoreStub.user.id = 0
        p = Projects()
        self.assertFalse(p.is_project_owner("project", "nobody"))
        self.assertTrue(dbStub.closed)

    def test_get_enabled_services(self):
        p = Projects()
        services = p.getEnabledServices(self)
        self.assertTrue(len(services) >= 3)
        self.assertIn('versioncontrol|svn|false|Subversion', services)
        self.assertIn('documenting|wiki|true|Wiki', services)
        self.assertIn('tasks|trac|true|Task management system', services)

    # TODO
    #def test_get_forkable_projects(self):
        #api = multiproject.common.projects.api.Projects()
        #conf.use_test_db(True)
        #self.load_fixtures()
        #forkables = api.get_forkable_projects("testuser")

        ## Testuser can fork project that he owns and the public project
        #self.assertEquals(len(forkables), 3)

    # dummy environment.is_component_enabled
    def is_component_enabled(self, component):
        return True


class ProjectTestCase(CQDETestCase):
    def setUp(self):
        pass

    def tearDown(self):
        dbStub.reset()
        conf.use_test_db(False)

    def test_validate(self):
        invalid_identifier = Project(1, u'testi_', u'testi_', u'Long name', 1, None)
        toolong_identifier = Project(1, u'asdfghjklqwertyuiopzxcvbnmasdfahg', u'asdfghjklqwertyuiopzxcvbnmasdfahg', u'Long name', 1, None)

        # Test invalid identifier
        msg = ""
        try:
            invalid_identifier.validate()
        except ProjectValidationException as exc:
            msg = exc.value
        self.assertTrue(msg.startswith("Identifier can not start or end with underscore"))

        # Test too long identifier
        msg = ""
        try:
            toolong_identifier.validate()
        except ProjectValidationException as exc:
            msg = exc.value
        self.assertTrue(msg.startswith("Too long project indentifier. L"))
