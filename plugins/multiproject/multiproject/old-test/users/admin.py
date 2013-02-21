# -*- coding: utf-8 -*-
import multiproject.home.admin.users
import trac.core
from multiproject.tests.ConfigurationStub import conf, userstoreStub
import multiproject.core.users
from multiproject.core.test.cqdetestcase import CQDETestCase

class DummyReq(object):
    def __init__(self):
        self.args = {
            'username': 'user',
            'password': 'password',
            'confirmpw': 'password',
            'mail': 'email',
            'lastName': 'User',
            'auth': 'on',
            'local': 'on',
        }

        class DummyPerm(object):
            def require(self, rights):
                pass

        self.perm = DummyPerm()
        self.method = 'post'
        self.authname = 'admin'

class CreateUserAdminPanelTestCase(CQDETestCase):

    def setUp(self):
        self.cm = trac.core.ComponentManager()
        self.req = DummyReq()
        self.orig_createIcon = multiproject.core.users.User.createIcon
        multiproject.core.users.User.createIcon = userstoreStub.user.createIcon

    def tearDown(self):
        self.cm = None
        self.req = None
        userstoreStub.reset()
        multiproject.core.users.User.createIcon = self.orig_createIcon

    def test_render_admin_panel(self):
        userstoreStub.userexists = False
        c = multiproject.home.admin.local_user.CreateLocalUserAdminPanel(self.cm)
        c.env = self; c.env.log = self
        c._send_notification = self._send_notification
        page, args = c.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_user_create.html')
        self.assertTrue(args.has_key('msg'))
        self.assertEquals(args['msg'], 'User created!')

    def test_render_admin_panel_user_exists(self):
        c = multiproject.home.admin.local_user.CreateLocalUserAdminPanel(self.cm)
        c.env = self; c.env.log = self
        page, args = c.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_user_create.html')
        self.assertTrue(args.has_key('msg'))
        self.assertEquals(args['msg'], 'Username already reserved!')

    # dummy log.debug
    def debug(self, msg):
        pass

    # dummy CreateLocalUserAdminPanel._send_notification
    def _send_notification(self, user):
        pass

class RemoveUsersTestCase(CQDETestCase):

    def setUp(self):
        self.cm = trac.core.ComponentManager()
        self.req = DummyReq()

    def tearDown(self):
        self.cm = None
        self.req = None
        userstoreStub.reset()

    def test_render_admin_panel(self):
        c = multiproject.home.admin.users.RemoveUsers(self.cm)
        c.env = self; c.env.log = self
        conf.allow_ldap_user_administration = True
        page, args = c.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_remove.html')
        self.assertTrue(args.has_key('msg'))
        self.assertNotEquals(args['msg'].find("User 'user' succesfully removed from auth store"), -1)
        self.assertNotEquals(args['msg'].find("User 'user' succesfully removed from local user store"), -1)

    def test_render_admin_panel_no_user(self):
        userstoreStub.userexists = False
        c = multiproject.home.admin.users.RemoveUsers(self.cm)
        c.env = self; c.env.log = self
        page, args = c.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_remove.html')
        self.assertTrue(args.has_key('msg'))
        self.assertNotEquals(args['msg'].find("No such user exist on LDAP"), -1)
        self.assertNotEquals(args['msg'].find("No such user exist locally"), -1)

    # dummy log.debug
    def debug(self, msg):
        pass
