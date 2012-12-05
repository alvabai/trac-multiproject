# -*- coding: utf-8 -*-
import multiproject.home.admin.users
import trac.core
from multiproject.tests.ConfigurationStub import userstoreStub, dbStub
from multiproject.core.test.cqdetestcase import CQDETestCase

userlist_result = [
    # username, givenname, lastname, email, mobile
    {'username' : "name1", 'first' : "Name1", 'last' : "Lastname1", 'email' : "name1@firma.fi", 'mobile' : "12345"},
    {'username' : "name2", 'first' : "Name2", 'last' : "Lastname2", 'email' : "name2@firma.fi", 'mobile' : "67890"}
]

class DummyReq(object):
    def __init__(self):
        self.args = {}

        class DummyPerm(object):
            def require(self, rights):
                pass

        self.perm = DummyPerm()
        self.href = trac.web.Href('/tmp') #@UndefinedVariable
        self.chrome = {}
        self.method = ""
        self.base_path = "path"

class EditUsersTestCase(CQDETestCase):

    def setUp(self):
        userstoreStub.all_users = userlist_result
        self.cm = trac.core.ComponentManager()
        self.req = DummyReq()

    def setUp_save(self):
        self.req.args = {
            'username' : 'somebody',
            'first' : 'first',
            'last' : 'last',
            'email' : 'no@mail.fi',
            'mobile' : '12345',
            'icon' : u'',
            'password' : 'password',
            'confirmpw' : 'password',
        }
        self.req.method = "POST"
        userstoreStub.user.givenName = "somebody"
        userstoreStub.user.authorization_key = 1
        userstoreStub.user.organization_keys = [ 1 ]

    def tearDown(self):
        self.cm = None
        self.req = None
        userstoreStub.reset()
        dbStub.reset()

    def test_show_list(self):
        p = multiproject.home.admin.users.EditUsersAdminPanel(self.cm)
        page, data = p.show_list(self.req, "test msg")
        self.assertEquals(page, 'admin_edit.html')
        self.assertEquals(data['msg'], "test msg")
        self.assertEquals(len(data['users']), 2)
        self.assertEquals(data['users'][0]['username'], "name1")
        self.assertEquals(data['users'][1]['mobile'], "67890")

    def test_show_list_error(self):
        userstoreStub.all_users = None
        p = multiproject.home.admin.users.EditUsersAdminPanel(self.cm)
        page, data = p.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_edit.html')
        self.assertTrue(not data['users'] or len(data['users']) == 0)

    def test_edit(self):
        # Set organization id
        dbStub.addResult([[1]])
        self.req.args['username'] = 'name'
        userstoreStub.user.givenName = "somebody"
        p = multiproject.home.admin.users.EditUsersAdminPanel(self.cm)
        p.env = self; p.env.log = self
        page, data = p.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_edit.html')
        self.assertEquals(data['first'], "somebody")

    def test_save(self):
        # Set organization id
        dbStub.addResult([[1]])
        self.setUp_save()
        p = multiproject.home.admin.users.EditUsersAdminPanel(self.cm)
        p.env = self; p.env.log = self
        page, data = p.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_edit.html')
        self.assertEquals(data['msg'], "User somebody updated!")

    def test_save_error_confirm_password(self):
        # Set organization id
        dbStub.addResult([[1]])
        self.setUp_save()
        p = multiproject.home.admin.users.EditUsersAdminPanel(self.cm)
        p.env = self; p.env.log = self

        self.req.args['confirmpw'] = "asdf"
        page, data = p.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_edit.html')
        self.assertEquals(data['msg'], "Passwords don't match!")

    def test_save_error_password_length(self):
        # Set organization id
        dbStub.addResult([[1]])
        dbStub.addResult([[1]])
        self.setUp_save()
        p = multiproject.home.admin.users.EditUsersAdminPanel(self.cm)
        p.env = self; p.env.log = self

        self.req.args['password'] = "asdf"
        page, data = p.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_edit.html')
        self.assertEquals(data['msg'], "Password should be at least 7 characters long!")

    def test_save_error_missing_last_name(self):
        # Set organization id
        dbStub.addResult([[1]])
        self.setUp_save()
        p = multiproject.home.admin.users.EditUsersAdminPanel(self.cm)
        p.env = self; p.env.log = self

        self.req.args['last'] = ""
        page, data = p.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_edit.html')
        self.assertEquals(data['msg'], "Last name required")

    def test_save_error_missing_email(self):
        # Set organization id
        dbStub.addResult([[1]])
        self.setUp_save()
        p = multiproject.home.admin.users.EditUsersAdminPanel(self.cm)
        p.env = self; p.env.log = self

        self.req.args['email'] = ""
        page, data = p.render_admin_panel(self.req, None, None, None)
        self.assertEquals(page, 'admin_edit.html')
        self.assertEquals(data['msg'], "E-mail address required")
