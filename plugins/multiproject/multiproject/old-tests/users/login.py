# -*- coding: utf-8 -*-
import multiproject.common.users.login
import trac.core
from multiproject.tests.ConfigurationStub import dbStub, conf
from Cookie import SimpleCookie as Cookie
from multiproject.core.test.cqdetestcase import CQDETestCase

class DummySession(dict):
    def save(self):
        pass


class DummyReq(object):
    def __init__(self):
        self.outcookie = Cookie()
        self.incookie = Cookie()
        self.args = {
            'username': 'user',
            'password': 'pass',
            'action': ''
        }
        self.authname = 'anonymous'
        self.remote_addr = '127.0.0.1'
        self.session = DummySession()
        self.base_path = ''
        self.remote_user = ''
        self.href = trac.web.Href('/tmp') #@UndefinedVariable
        self.chrome = {}
        self.method = ''

    def redirect(self, uri):
        pass

class GlobalLoginModuleTestCase(CQDETestCase):

    def setUp(self):
        conf.use_test_db(False)
        dbStub.addResult([['cookiename']])
        self.cm = trac.core.ComponentManager()
        self.cookie = Cookie()
        self.cookie.value = 'cookie'
        self.req = DummyReq()
        self.secure_cookies = True

    def tearDown(self):
        dbStub.reset()
        self.cm = None
        self.cookie = None
        self.req = None

    def test_get_name_for_cookie(self):
        g = multiproject.common.users.login.GlobalLoginModule(self.cm)
        g.env = self; g.env.log = self
        self.assertEquals(g._get_name_for_cookie(self.req, self.cookie), 'cookiename')
        self.assertTrue(dbStub.closed)

    def test_get_name_for_cookie_error(self):
        dbStub.setExceptions(True)
        g = multiproject.common.users.login.GlobalLoginModule(self.cm)
        g.env = self; g.env.log = self
        self.assertEquals(g._get_name_for_cookie(self.req, self.cookie), None)
        self.assertTrue(dbStub.closed)

    def test_do_logout(self):
        g = multiproject.common.users.login.GlobalLoginModule(self.cm)
        g.env = self; g.env.log = self
        g._do_logout(self.req)
        self.assertTrue(dbStub.closed)

    # TODO
    #def test_do_login(self):
        #g = multiproject.common.users.login.GlobalLoginModule(self.cm)
        #g.env = self; g.env.log = self
        #g._do_login(self.req)
        #self.assertTrue(dbStub.closed)

    def test_authenticate(self):
        g = multiproject.common.users.login.GlobalLoginModule(self.cm)
        g.env = self; g.env.log = self
        self.assertEquals(g.authenticate(self.req), None)
        self.req.remote_user = 'remote'
        self.assertEquals(g.authenticate(self.req), 'remote')
        self.req.incookie['trac_auth'] = 'test'
        self.assertEquals(g.authenticate(self.req), 'cookiename')
        self.assertTrue(dbStub.closed)

    def test_process_request(self):
        g = multiproject.common.users.login.GlobalLoginModule(self.cm)
        self.req.args['action'] = 'login'
        page, data, tmp = g.process_request(self.req) #@UnusedVariable
        self.assertEquals(page, 'multiproject_login.html')

    # dummy log.debug
    def debug(self, msg):
        pass
