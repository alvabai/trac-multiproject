from multiproject.core.auth.basic_access import BasicAccessControl
from multiproject.core.stubs import DummyReq
from ...ConfigurationStub import conf
from multiproject.core.test.cqdetestcase import CQDETestCase

class BasicAccessTest(CQDETestCase):
    def setUp(self):
        conf.use_test_db(False)

    def tearDown(self):
        conf.use_test_db(False)

    def testInit(self):
        conf.use_test_db(True)
        self.load_fixtures()

        # Simple test case to confirm that initially works 
        req = DummyReq('cartman', 'cartmans_pw', 'GET', '/storageauthtest/login/xmlrpc', '')
        basic = BasicAccessControl(req)

        self.assertEquals(basic.username, 'cartman')
        self.assertEquals(basic.plain_pw, 'cartmans_pw')
        self.assertEquals(basic.req, req)

    def testNotImplementedError(self):
        conf.use_test_db(True)
        self.load_fixtures()

        req = DummyReq('cartman', 'cartmans_pw', 'GET', '/storageauthtest/login/xmlrpc', '')
        basic = BasicAccessControl(req)

        # Some methods are implemented in subclasses and so should throw NotImplementedError
        self.assertRaises(NotImplementedError, basic.has_permission)
        self.assertRaises(NotImplementedError, basic.environment_identifier)
        self.assertRaises(NotImplementedError, basic.is_read)
        self.assertRaises(NotImplementedError, basic.read_action)
        self.assertRaises(NotImplementedError, basic.write_action)

        # Normal assertRaises does not work with @properties
        throws = False
        try:
            basic.required_action
        except NotImplementedError:
            throws = True
        self.assertTrue(throws)

        throws = False
        try:
            basic.environment_key
        except NotImplementedError:
            throws = True
        self.assertTrue(throws)

    def testAuthentication(self):
        conf.use_test_db(True)
        self.load_fixtures()

        req = DummyReq('cartman', 'cartmans_pw', 'GET', '/storageauthtest/login/xmlrpc', '')
        basic = BasicAccessControl(req)
        self.assertTrue(basic.is_authentic())

        req = DummyReq('cartman', 'cartmanspw', 'GET', '/storageauthtest/login/xmlrpc', '')
        basic = BasicAccessControl(req)
        self.assertFalse(basic.is_authentic())

        req = DummyReq('user@nomail.box', 'nomailforme', 'GET', '/storageauthtest/login/xmlrpc', '')
        basic = BasicAccessControl(req)
        self.assertTrue(basic.is_authentic())

        req = DummyReq('user%40nomail.box', 'nomailforme', 'GET', '/storageauthtest/login/xmlrpc', '')
        basic = BasicAccessControl(req)
        self.assertTrue(basic.is_authentic())

        req = DummyReq('user@nomail.box', 'wrongpw', 'GET', '/storageauthtest/login/xmlrpc', '')
        basic = BasicAccessControl(req)
        self.assertFalse(basic.is_authentic())

        req = DummyReq('user%40nomail.box', 'wrongpw', 'GET', '/storageauthtest/login/xmlrpc', '')
        basic = BasicAccessControl(req)
        self.assertFalse(basic.is_authentic())

    def testPathParser(self):
        dav = BasicAccessControl(DummyReq('test', 'passwd', 'GET', '/dav/davprj', ''))
        self.assertEquals(dav.parse_identifier_from_uri(), 'davprj')

        svn = BasicAccessControl(DummyReq('test', 'passwd', 'GET', '/svn/svnprj', ''))
        self.assertEquals(svn.parse_identifier_from_uri(), 'svnprj')

        svn = BasicAccessControl(DummyReq('test', 'passwd', 'GET', '/svn/tasaasdfaf/!svn/vcc/default', ''))
        self.assertEquals(svn.parse_identifier_from_uri(), 'tasaasdfaf')

        git = BasicAccessControl(DummyReq('test', 'passwd', 'GET', '/git/gitprj', ''))
        self.assertEquals(git.parse_identifier_from_uri(), 'gitprj')

    def testUsernames(self):
        basic = BasicAccessControl(DummyReq('test@user.com', 'passwd', 'GET', '/svn/svnprj', ''))
        self.assertEquals(basic.username, 'test@user.com')

        basic = BasicAccessControl(DummyReq('test%40user.com', 'passwd', 'GET', '/svn/svnprj', ''))
        self.assertEquals(basic.username, 'test@user.com')

        basic = BasicAccessControl(DummyReq('test', 'passwd', 'GET', '/svn/svnprj', ''))
        self.assertEquals(basic.username, 'test')
