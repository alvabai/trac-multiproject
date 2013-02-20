# -*- coding: utf-8 -*-
from multiproject.core.test.cqdetestcase import CQDETestCase
import multiproject.common.users.preferences
import trac.core
import multiproject.core.users
from multiproject.tests.ConfigurationStub import userstoreStub, dbStub

class DummyReq(object):
    def __init__(self):
        self.args = {
            'icon': '',
            'mail': 'email',
            'lastName': 'User',
            'newpassword': 'password',
            'confirmpw': 'password',
            'oldpassword': 'oldpass'
        }
        self.method = 'POST'
        self.base_path = 'path'
        self.authname = 'authname'

class UserImagePreferencePanelTestCase(CQDETestCase):

    def setUp(self):
        self.cm = trac.core.ComponentManager()
        self.req = DummyReq()
        self.orig_createIcon = multiproject.core.users.User.createIcon
        multiproject.core.users.User.createIcon = userstoreStub.user.createIcon
        userstoreStub.user.username = 'username'

    def tearDown(self):
        self.cm = None
        self.req = None
        userstoreStub.reset()
        multiproject.core.users.User.createIcon = self.orig_createIcon

    def test_render_preference_panel(self):
        u = multiproject.common.users.preferences.UserImagePreferencePanel(self.cm)
        page, data = u.render_preference_panel(self.req, None)
        self.assertEquals(page, 'multiproject_user_prefs_image.html')
        self.assertEquals(data['user'].username, 'username')
        self.assertEquals(data['base_path'], 'path')

    def test_remove_icon(self):
        userstoreStub.user.icon = "icon"
        self.req.args['removeicon'] = "removeicon"
        u = multiproject.common.users.preferences.UserImagePreferencePanel(self.cm)
        page, data = u.render_preference_panel(self.req, None)
        self.assertEquals(page, 'multiproject_user_prefs_image.html')
        self.assertEquals(data['user'].username, 'username')
        self.assertEquals(data['base_path'], 'path')
        self.assertEquals(userstoreStub.user.icon, None)

class UserBasicInfoTestCase(CQDETestCase):

    def setUp(self):
        self.cm = trac.core.ComponentManager()
        self.req = DummyReq()
        userstoreStub.user.username = 'username'

    def tearDown(self):
        self.cm = None
        self.req = None
        userstoreStub.reset()

    def test_render_preference_panel(self):
        self.req.method = ''
        u = multiproject.common.users.preferences.UserBasicInfo(self.cm)
        page, data = u.render_preference_panel(self.req, None)
        self.assertEquals(page, 'multiproject_user_prefs_basic.html')
        self.assertFalse(data.has_key('msg'))
        self.assertEquals(data['user'].username, 'username')

    def test_render_preference_panel_do_save(self):
        u = multiproject.common.users.preferences.UserBasicInfo(self.cm)
        u.env = self; u.env.log = self
        page, data = u.render_preference_panel(self.req, None)
        self.assertEquals(page, 'multiproject_user_prefs_basic.html')
        self.assertEquals(data['msg'], 'Information updated!')
        self.assertEquals(data['user'].username, 'username')

class UserChangePasswordTestCase(CQDETestCase):

    def setUp(self):
        self.cm = trac.core.ComponentManager()
        self.req = DummyReq()
        userstoreStub.user.username = 'username'
        userstoreStub.user.authorization_key = 1
        userstoreStub.user.organization_keys = [ 1 ]
        dbStub.addResult([[1]])

    def tearDown(self):
        self.cm = None
        self.req = None
        userstoreStub.reset()
        dbStub.reset()

    def test_render_preference_panel(self):
        self.req.method = ''
        u = multiproject.common.users.preferences.UserPasswordPreferencePanel(self.cm)
        u.env = self; u.env.log = self
        page, data = u.render_preference_panel(self.req, None)
        self.assertEquals(page, 'multiproject_user_prefs_password.html')
        self.assertFalse(data.has_key('msg'))

    def test_change_password(self):

        u = multiproject.common.users.preferences.UserPasswordPreferencePanel(self.cm)
        u.env = self; u.env.log = self
        page, data = u.render_preference_panel(self.req, None)
        self.assertEquals(page, 'multiproject_user_prefs_password.html')
        self.assertEquals(data['msg'], "Password changed!")

    def test_change_password_error(self):
        u = multiproject.common.users.preferences.UserPasswordPreferencePanel(self.cm)
        u.env = self; u.env.log = self

        self.req.args['confirmpw'] = 'asdf'
        page, data = u.render_preference_panel(self.req, None)
        self.assertEquals(page, 'multiproject_user_prefs_password.html')
        self.assertEquals(data['msg'], "New password does not match with confirmation!")

        self.req.args['newpassword'] = 'asdf'
        page, data = u.render_preference_panel(self.req, None)
        self.assertEquals(page, 'multiproject_user_prefs_password.html')
        self.assertEquals(data['msg'], "New password should be at least 7 characters long!")

        self.req.args['oldpassword'] = ""
        page, data = u.render_preference_panel(self.req, None)
        self.assertEquals(page, 'multiproject_user_prefs_password.html')
        self.assertEquals(data['msg'], "Old password is invalid!")
