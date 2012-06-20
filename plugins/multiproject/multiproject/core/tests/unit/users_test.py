from multiproject.core.cache.user_cache import UserCache
from multiproject.core.test.cqdetestcase import CQDETestCase
import ldap
import multiproject.core.users
from ..ConfigurationStub import dbStub, conf


class DummyIcon(object):
    def __init__(self):
        self.value = "asdf"
        self.filename = "jklm"
        self.type = "png"


class UserTestCase(CQDETestCase):

    def setUp(self):
        conf.use_test_db(False)
        dbStub.addResult([[1]])

    def tearDown(self):
        dbStub.reset()

    def test_get_display_name(self):
        u = multiproject.core.users.User()
        u.username = 'username'
        u.givenName = 'First'
        u.lastName = 'Last'
        u.mail = 'user@somewhere'

        conf.display_name = ["username"]
        self.assertEquals(u.getDisplayName(), "username")

        conf.display_name = ["firstname"]
        self.assertEquals(u.getDisplayName(), "First")

        conf.display_name = ["firstname", " ", "lastname"]
        self.assertEquals(u.getDisplayName(), "First Last")

        conf.display_name = ["lastname", " ", "(", "mail", ")"]
        self.assertEquals(u.getDisplayName(), "Last (user@somewhere)")

    def test_create_icon(self):
        u = multiproject.core.users.User()
        u.createIcon(DummyIcon())

        self.assertEquals(u.icon, 1)
        self.assert_(dbStub.closed, "dbStub is not closed!")

    def test_create_icon_error(self):
        dbStub.setExceptions(True)
        u = multiproject.core.users.User()
        u.createIcon(DummyIcon())

        self.assertEquals(u.icon, None)
        self.assert_(dbStub.closed)

class MySqlUserStoreTestCase(CQDETestCase):

    def setUp(self):
        dbStub.addResult([
            # id, username, email, mobile, givenname, lastname, icon, pwHash (='password'), insider
            [1, "name", "name@firma.fi", "12345", "Name", "Lastname",
             None, "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8", 0,0,0]
        ])
        self._user = multiproject.core.users.User()
        self._user.id = 1
        self._user.username = 'tester'
        self._user.givenName = 'First'
        self._user.lastName = 'Last'
        self._user.mail = ''
        self._user.mobile = ''
        self._user.password = 'password'
        #self._user.account_type = self._user.LOCAL_USER
        self.cache = UserCache.instance()

    def tearDown(self):
        dbStub.reset()
        self._user = None
        self.cache.clearUser('name')

    def test_get_user(self):
        m = multiproject.core.users.MySqlUserStore()

        user = m.getUser('name')
        self.assertEquals(user.username, 'name')
        self.assertTrue(dbStub.closed)

        # second pass should come from cache (no db hit)
        dbStub.reset()
        user = m.getUser('name')
        self.assertEquals(user.username, 'name')
        self.assertFalse(dbStub.closed)

    def test_get_user_error(self):
        dbStub.setExceptions(True)
        m = multiproject.core.users.MySqlUserStore()
        self.cache.clearUser('test')

        self.assertEquals(m.getUser('test'), None)
        self.assertTrue(dbStub.closed)

    def test_delete_user(self):
        m = multiproject.core.users.MySqlUserStore()
        self.assertTrue(m.deleteUser(self._user))
        self.assertTrue(dbStub.closed)

    def test_delete_user_error(self):
        dbStub.setExceptions(True)
        m = multiproject.core.users.MySqlUserStore()
        self.assertFalse(m.deleteUser(self._user))
        self.assertTrue(dbStub.closed)

    def test_store_user(self):
        m = multiproject.core.users.MySqlUserStore()
        self.assertTrue(m.storeUser(self._user))
        self.assertTrue(dbStub.closed)

    def test_store_user_error(self):
        dbStub.setExceptions(True)
        m = multiproject.core.users.MySqlUserStore()
        self.assertFalse(m.storeUser(self._user))
        self.assertTrue(dbStub.closed)

    def test_update_user(self):
        m = multiproject.core.users.MySqlUserStore()
        self.assertTrue(m.updateUser(self._user))
        self.assertTrue(dbStub.closed)

    def test_update_user_error(self):
        dbStub.setExceptions(True)
        m = multiproject.core.users.MySqlUserStore()
        self.assertFalse(m.updateUser(self._user))
        self.assertTrue(dbStub.closed)

    def test_update_password(self):
        m = multiproject.core.users.MySqlUserStore()
        self.assertTrue(m.updatePassword(self._user, 'newpassword'))
        self.assertTrue(dbStub.closed)

    def test_update_password_error(self):
        dbStub.setExceptions(True)
        m = multiproject.core.users.MySqlUserStore()
        self.assertFalse(m.updatePassword(self._user, 'newpassword'))
        self.assertTrue(dbStub.closed)
        self.assertFalse(m.updatePassword(self._user, None))
        self._user.id = None
        self.assertFalse(m.updatePassword(self._user, 'newpassword'))

    def test_compare_password(self):
        self._user.pwHash = '5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8' # 'password'
        m = multiproject.core.users.MySqlUserStore()
        self.assertTrue(m._compare_password(self._user, 'password'))
        self.assertFalse(m._compare_password(self._user, 'invalid'))

    def test_user_exists(self):
        m = multiproject.core.users.MySqlUserStore()
        self.cache.clearUser('test')
        self.assertTrue(m.userExists('anonymous'))
        self.assertTrue(m.userExists('test'))
        self.assertTrue(m.userExists('test', 'password'))
        self.assertFalse(m.userExists('test', 'invalid'))

    # dummy log.debug
    def debug(self, msg):
        pass


class DummyLdap(object):
    def __init__(self):
        self.protocol_version = None
        self.username = None
        self.password = None
        self.unbind_called = False
        self.delete_called = False
        self.add_called = False
        self.searchresult = [['user', {
            'uid': ['username'],
            'surname': ['Lastname'],
            'mail': ['email'],
            'userPassword': ['pass'],
            'gn': ['Firstname'],
            'mobile': ['12345']
        }]]

    def simple_bind_s(self, username=None, password=None):
        self.username = username
        self.password = password

    def unbind(self):
        self.unbind_called = True

    def delete(self, user_dn):
        self.delete_called = True

    def search_s(self, dn, scope, filter, attr):
        return self.searchresult

    def add_s(self, user_dn, user_record):
        self.add_called = True

class LdapUserStoreTestCase(CQDETestCase):

    def setUp(self):
        dbStub.addResult([
            # id, username, email, mobile, givenname, lastname, icon, pwHash (='password'), insider
            [1, "name", "name@firma.fi", "12345", "Name", "Lastname",
             None, "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8", 0]
        ])
        self._user = multiproject.core.users.User()
        self._user.id = 1
        self._user.username = 'tester'
        self._user.givenName = 'First'
        self._user.lastName = 'Last'
        self._user.mail = ''
        self._user.mobile = ''
        self._user.password = 'password'
        self.orig_initialize = ldap.initialize
        ldap.initialize = self.ldap_initialize
        self.ldap = DummyLdap()

    def tearDown(self):
        dbStub.reset()
        self._user = None
        self.ldap = None
        ldap.initialize = self.orig_initialize

    def test_connect(self):
        l = multiproject.core.users.LdapUserStore()
        l._connect('user', 'pass')
        self.assertEquals(self.ldap.username, 'user')
        self.assertEquals(self.ldap.password, 'pass')

    def test_close(self):
        l = multiproject.core.users.LdapUserStore()
        l._connect()
        l._close()
        self.assertTrue(self.ldap.unbind_called)

    def test_search_user(self):
        l = multiproject.core.users.LdapUserStore()
        result = l._search_user('user')
        self.assertEquals(result.get_dn(), 'user')

    def test_get_user(self):
        l = multiproject.core.users.LdapUserStore()
        user = l.getUser('user')
        self.assertEquals(user.username, 'username')
        self.assertEquals(user.lastName, 'Lastname')
        self.assertEquals(user.givenName, 'Firstname')
        self.assertEquals(user.pwHash, 'pass')
        self.assertEquals(user.mobile, '12345')

    def test_get_user_error(self):
        self.ldap.searchresult = []
        l = multiproject.core.users.LdapUserStore()
        self.assertEquals(l.getUser('user'), None)

    def test_user_exists(self):
        l = multiproject.core.users.LdapUserStore()
        self.assertTrue(l.userExists('user'))
        self.assertTrue(l.userExists('user', 'pass'))

    def test_user_exists_error(self):
        self.ldap.searchresult = []
        l = multiproject.core.users.LdapUserStore()
        self.assertFalse(l.userExists('user'))
        self.assertFalse(l.userExists('user', 'pass'))

    def test_delete_user(self):
        l = multiproject.core.users.LdapUserStore()
        user = multiproject.core.users.User()
        user.username = 'user'
        self.assertTrue(l.deleteUser(user))
        self.assertTrue(self.ldap.delete_called)

    def test_store_user(self):
        self.ldap.searchresult = []
        l = multiproject.core.users.LdapUserStore()
        user = multiproject.core.users.User()
        user.username = u'user'
        user.lastName = u'last'
        user.password = u'pass'
        user.mail = u'email'
        user.givenName = u'first'
        user.mobile = u'12345'
        self.assertTrue(l.storeUser(user)) # user didn't exist
        self.assertTrue(self.ldap.add_called)

    def test_store_user_error(self):
        l = multiproject.core.users.LdapUserStore()
        user = multiproject.core.users.User()
        user.username = u'user'
        self.assertFalse(l.storeUser(user)) # user already exists
        self.assertFalse(self.ldap.add_called)

    def test_compare_password(self):
        l = multiproject.core.users.LdapUserStore()
        user = multiproject.core.users.User()
        user.pwHash = '{MD5}Gh3JHJBzJcaScd3wyUS8cg==' # 'pass'
        self.assertFalse(l.comparePassword(user, 'password'))
        self.assertTrue(l.comparePassword(user, 'pass'))
        user.pwHash = '{CRYPT}abccBcrPOxnLU' # 'pass'
        self.assertFalse(l.comparePassword(user, 'password'))
        self.assertTrue(l.comparePassword(user, 'pass'))

    # dummy ldap.initialize
    def ldap_initialize(self, path):
        return self.ldap

    #dummy log.debug
    def debug(self, msg):
        pass
