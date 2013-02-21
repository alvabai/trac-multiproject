# -*- coding: utf-8 -*-
from multiproject.core.test.cqdetestcase import CQDETestCase
import multiproject.home.frontpage.welcome
import trac.core
from multiproject.tests.ConfigurationStub import dbStub, userstoreStub
from Cookie import SimpleCookie as Cookie
from multiproject.core.stubs import DummyEnv

class DummySession(dict):
    def save(self):
        pass


class DummyReq(object):
    def __init__(self):
        self.authname = 'authname'
        self.base_path = 'path'
        self.base_url = '/test'
        self.path_info = '/path'
        self.href = trac.web.Href('/tmp') #@UndefinedVariable
        self.chrome = {}
        self.incookie = Cookie()
        self.uri = "/test"
        self.session = DummySession()
        self.perm = {}

def _wikipage(req):
    return None

class WelcomeModuleTestCase(CQDETestCase):

    def setUp(self):
        dbStub.addResult([])
        self.cm = trac.core.ComponentManager()
        self.req = DummyReq()
        self.path = '/tmp' # dummy env.path

    def tearDown(self):
        dbStub.reset()
        userstoreStub.reset()
        self.cm = None
        self.req = None

    def test_process_request(self):
        userstoreStub.user.username = 'username'
        userstoreStub.user.id = 234791
        userstoreStub.user.authorization_key = 5
        userstoreStub.user.organization_keys = [ 5 ]

        p = multiproject.home.frontpage.welcome.WelcomeModule(self.cm)
        p.env = DummyEnv(self.req)
        p._get_welcome_page = _wikipage

        page, data, tmp = p.process_request(self.req) #@UnusedVariable
        self.assertEquals(page, 'welcome.html')
        self.assertEquals(data['base_path'], 'path')
        self.assertTrue(data.has_key('mostactiveprojects'))
        self.assertTrue(data.has_key('newestprojects'))
        self.assertTrue(data.has_key('latest_events'))
        self.assertTrue(dbStub.closed)

    def test_process_request_anonymous(self):
        userstoreStub.user.username = 'anonymous'
        userstoreStub.user.id = 234791
        self.req.authname = 'anonymous'

        p = multiproject.home.frontpage.welcome.WelcomeModule(self.cm)
        p.env = DummyEnv(self.req)
        p._get_welcome_page = _wikipage

        page, data, tmp = p.process_request(self.req) #@UnusedVariable
        self.assertEquals(page, 'welcome.html')
        self.assertEquals(data['base_path'], 'path')
