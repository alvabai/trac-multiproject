# -*- coding: utf-8 -*-
import multiproject.common.xmlrpc
import trac.core
from multiproject.tests.ConfigurationStub import conf, dbStub
from multiproject.core.test.cqdetestcase import CQDETestCase

project_search_result = [
    [1, "Project 1", "project1", "descr1", 10, "2009-01-01", "2009-01-01", "2009-01-01", None, None, 1 ],
    [2, "Project 2", "project2", "descr2", 11, "2009-01-02", "2009-01-01", "2009-01-01", None, None, 2 ],
    [3, "Project 3", "project3", "descr3", 12, "2009-01-03", "2009-01-01", "2009-01-01", None, None, 3 ]
]

test_contexts = [
    [1, "context1", "context1"],
    [2, "context2", "context2"]
]

test_categories = [
    [1, "cat1", "cat1", None, 1],
    [2, "cat2", "cat2", None, 1],
    [3, "cat3", "cat3", None, 1]
]

class Components(object):
    def __init__(self):
        return

    def get(self, cls):
        return LocalEnv()


class LocalRepo(object):
    def __init__(self):
        self.name = "svn:/path/to/somewhere"

    def get_node(self):
        return


class LocalEnv(object):
    def __init__(self):
        self.components = Components()
        self.repository_type = "svn"

    def setUp(self):
        return

    def tearDown(self):
        return

    def get_repository(self, arg1):
        return LocalRepo()

class ProjectsRPCTestCase(CQDETestCase):

    def setUp(self):
        self.cm = trac.core.ComponentManager()
        self.authname = 'dummyUsername'

    def tearDown(self):
        dbStub.reset()
        self.cm = None

    def is_component_enabled(self, component):
        return True

    def test_xmlrpc_namespace(self):
        g = multiproject.common.xmlrpc.ProjectsRPC(self.cm)
        result = g.xmlrpc_namespace()
        self.assertEquals(result, 'projects')

    def test_authorizationCheck(self):
        g = multiproject.common.xmlrpc.UserRPC(self.cm)
        result = g.authorizationCheck(self)
        self.assertEquals(result, 1038)

    def test_getCount(self):
        dbStub.addResult([ [198] ])
        g = multiproject.common.xmlrpc.ProjectsRPC(self.cm)
        result = g.getCount(self)
        self.assertEquals(result, 198)

    def test_getProjectCategories(self):
        dbStub.addResult(test_contexts)
        dbStub.addResult(test_categories)
        dbStub.addResult(test_categories)
        g = multiproject.common.xmlrpc.ProjectsRPC(self.cm)
        result = g.getProjectCategories(self)
        self.assertEquals(len(result), 4)
        self.assertEquals(result[0], "context1")
        self.assertEquals(result[2], "context2")
        self.assertEquals(len(result[1]), 3)
        self.assertEquals(len(result[3]), 3)
        self.assertEquals(result[1][0], "cat1")
        self.assertEquals(result[1][1], "cat2")
        self.assertEquals(result[1][2], "cat3")

    # TODO
    #def test_openProject(self):
        #g = multiproject.common.xmlrpc.ProjectsRPC(self.cm)
        #g.env = LocalEnv()
        #result = g.openProject(self, 'project_name', '', '')
        #expected = 'versioncontrol|svn|' + conf.default_http_scheme + "://" + conf.domain_name + '/svn/project_name'
        #self.assertEquals(result, [ expected ])

    def test_searchProjects(self):
        dbStub.addResult(project_search_result)
        g = multiproject.common.xmlrpc.ProjectsRPC(self.cm)
        result = g.searchProjects(self, 'project', 'category_not_used')
        self.assertEquals(len(result), 3)
        self.assertEquals(result[0], 'project1|Project 1')
        self.assertEquals(result[1], 'project2|Project 2')
        self.assertEquals(result[2], 'project3|Project 3')
        self.assertTrue(dbStub.closed)

    def test_joinProject(self):
        g = multiproject.common.xmlrpc.ProjectsRPC(self.cm)
        result = g.joinProject(self, 'project_name', 'reason')
        self.assertEquals(result, 0)

    def test_projectExists(self):
        dbStub.addResult([ [1] ])
        g = multiproject.common.xmlrpc.ProjectsRPC(self.cm)
        result = g.projectExists(self, 'project2')
        self.assertTrue(result)
        self.assertTrue(dbStub.closed)

    def test_getTracServices(self):
        g = multiproject.common.xmlrpc.ProjectsRPC(self.cm)
        g.env = self
        services = g.getTracServices(self)
        self.assertTrue(len(services) >= 3)
        self.assertIn('versioncontrol|svn|false|Subversion', services)
        self.assertIn('documenting|wiki|true|Wiki', services)
        self.assertIn('tasks|trac|true|Task management system', services)

