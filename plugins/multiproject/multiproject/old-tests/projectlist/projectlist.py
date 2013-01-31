# -*- coding: utf-8 -*-
from multiproject.core.test.cqdetestcase import CQDETestCase
import multiproject.home.projectlist.projectlist
import trac.core
from multiproject.tests.ConfigurationStub import dbStub, userstoreStub, conf
import multiproject.core.permissions

class DummyReq(object):
    def __init__(self):
        self.args = {
            'action': '',
            'project': 'projectname',
            'prj_short_name': u'short',
            'prj_long_name': 'long',
            'authrights': 'MODIFY'
        }
        self.authname = 'user'
        self.base_path = 'path'
        self.href = trac.web.Href('/tmp') #@UndefinedVariable
        self.chrome = {}

        class DummyPerm(dict):
            def require(self, rights):
                pass

        self.perm = DummyPerm()
        self.url = None

    def redirect(self, url):
        self.url = url

class ProjectListTestCase(CQDETestCase):

    def setUp(self):
        dbStub.addResult([[1]])
        dbStub.addResult([])
        self.cm = trac.core.ComponentManager()
        self.req = DummyReq()
        self.path = '/tmp' # dummy env.path
        self.project_name = "tmp"
        self.orig_create_project = multiproject.common.projects.api.Projects.create_project
        self.orig_remove_project = multiproject.common.projects.api.Projects.remove_project
        self.orig_get_project = multiproject.common.projects.api.Projects.get_project
        self.orig_is_superuser = multiproject.core.permissions.CQDESuperUserStore.is_superuser

    def tearDown(self):
        dbStub.reset()
        userstoreStub.reset()
        self.cm = None
        self.req = None
        multiproject.common.projects.api.Projects.create_project = self.orig_create_project
        multiproject.common.projects.api.Projects.remove_project = self.orig_remove_project
        multiproject.common.projects.api.Projects.get_project = self.orig_get_project
        multiproject.core.permissions.CQDESuperUserStore.is_superuser = self.orig_is_superuser

    def test_process_request(self):
        userstoreStub.user.username = 'user'
        userstoreStub.user.id = 234791
        userstoreStub.user.authorization_key = 5
        multiproject.core.permissions.CQDESuperUserStore.is_superuser = self.is_superuser
        conf.non_browsable_contexts = []
        p = multiproject.home.projectlist.projectlist.ProjectListModule(self.cm)

        page, data, tmp = p.process_request(self.req) #@UnusedVariable
        self.assertEquals(page, 'projectlist.html')
        self.assertEquals(data['username'], 'user')
        self.assertEquals(data['envurl'], 'path')
        self.assertFalse(data.has_key('msg'))
        self.assertTrue(dbStub.closed)

    def test_process_request_remove(self):
        self.req.path_info = "/remove"
        self.req.perm = ['TRAC_ADMIN']
        multiproject.common.projects.api.Projects.remove_project = self.remove_project
        multiproject.common.projects.api.Projects.get_project = self.get_project
        multiproject.core.permissions.CQDESuperUserStore.is_superuser = self.is_superuser

        userstoreStub.user.username = 'user'
        userstoreStub.user.id = 234791
        userstoreStub.user.authorization_key = 5

        p = multiproject.home.projectlist.projectlist.ProjectListModule(self.cm)
        p.env = self
        p.process_request(self.req)
        self.assertEquals(self.req.url, self.req.base_path + "/myprojects")
        self.assertTrue(dbStub.closed)

    def test_process_request_create(self):
        self.req.path_info = "/create"
        self.req.args['vcstype'] = 'svn'
        self.req.args['prj_short_name'] = 'short'
        self.req.args['prj_long_name'] = 'longname'

        multiproject.common.projects.api.Projects.create_project = self.create_project
        multiproject.core.permissions.CQDESuperUserStore.is_superuser = self.is_superuser
        p = multiproject.home.projectlist.projectlist.ProjectListModule(self.cm)
        p.process_request(self.req)
        self.assertEquals(self.req.url, conf.url_projects_path + "/" + "short")

    # dummy env.is_component_enabled
    def is_component_enabled(self, component):
        return True

    # dummy Projects.remove_project
    def remove_project(self, project):
        return "Project removed!"

    # dummy Projects.create_project
    def create_project(self, project, services):
        return ''

    #  dummy Projects.get_project
    def get_project(self, env_name):
        return multiproject.common.projects.api.Project(1, "env_name", "project_name", "description", 1, "2010-01-01")

    # dummy config.options
    def options(self, section):
        return []

    # dummy CQDESuperUserStore.is_superuser
    def is_superuser(self, username):
        return True
