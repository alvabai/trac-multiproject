from multiproject.core.auth.dav_access import DAVAccessControl
from multiproject.core.stubs import DummyReq
from ...ConfigurationStub import conf
from multiproject.core.test.cqdetestcase import CQDETestCase

class DavAccessControlTestCase(CQDETestCase):
    def setUp(self):
        conf.use_test_db(False)

    def tearDown(self):
        conf.use_test_db(False)

    def testDAVAccessControl(self):
        conf.use_test_db(True)
        self.load_fixtures()

        davaccess = DAVAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/dav/storageauthtest', ''))
        self.assertTrue(davaccess.is_authentic())
        self.assertTrue(davaccess.has_permission())

        davaccess = DAVAccessControl(DummyReq('kenny', 'ohmygod', 'GET', '/dav/storageauthtest', ''))
        self.assertTrue(davaccess.is_authentic())
        self.assertFalse(davaccess.has_permission())

        davaccess = DAVAccessControl(DummyReq('davreader', 'davreader_pw', 'POST', '/dav/storageauthtest', ''))
        self.assertTrue(davaccess.is_authentic())
        self.assertFalse(davaccess.has_permission())

        davaccess = DAVAccessControl(DummyReq('davreader', 'davreader_pw', 'GET', '/dav/storageauthtest', ''))
        self.assertTrue(davaccess.is_authentic())
        self.assertTrue(davaccess.has_permission())
