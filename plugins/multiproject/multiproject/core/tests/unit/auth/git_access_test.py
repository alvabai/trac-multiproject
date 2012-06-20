from multiproject.core.stubs import DummyReq
from ...ConfigurationStub import conf
from multiproject.core.test.cqdetestcase import CQDETestCase
from multiproject.core.auth.git_access import GITAccessControl

class GitAccessControlTestCase(CQDETestCase):
    def tearDown(self):
        conf.use_test_db(False)

    def testProjectIdentifier(self):
        conf.use_test_db(False)

        # Without .git
        gitaccess = GITAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/git/storageauthtest', ''))
        self.assertEquals(gitaccess.environment_identifier(), 'storageauthtest')

        gitaccess = GITAccessControl(DummyReq('kenny', 'ohmygod', 'GET', '/git/iahedfba/dsfgas', ''))
        self.assertEquals(gitaccess.environment_identifier(), 'iahedfba')

        # With .git
        gitaccess = GITAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/git/storageauthtest.git', ''))
        self.assertEquals(gitaccess.environment_identifier(), 'storageauthtest')

        gitaccess = GITAccessControl(DummyReq('kenny', 'ohmygod', 'GET', '/git/iahedfba.git/refs/HEAD', ''))
        self.assertEquals(gitaccess.environment_identifier(), 'iahedfba')

    def testIsRead(self):
        conf.use_test_db(False)

        # Simple read cases
        gitaccess = GITAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/git/storageauthtest', ''))
        self.assertTrue(gitaccess.is_read())

        gitaccess = GITAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/git/storageauthtest.git', ''))
        self.assertTrue(gitaccess.is_read())

        # Simple write cases
        gitaccess = GITAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/git/storageauthtest.git', 'service=git-receive-pack&some=other'))
        self.assertFalse(gitaccess.is_read())

        gitaccess = GITAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/git/storageauthtest.git', 'some=other&service=git-receive-pack'))
        self.assertFalse(gitaccess.is_read())

        gitaccess = GITAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/git/storageauthtest.git/refs/jotain/git-receive-pack', ''))
        self.assertFalse(gitaccess.is_read())


    def testAccess(self):
        conf.use_test_db(True)
        self.load_fixtures()

        # Cartman has read access to storageauthtest

        # Simple read cases when having read access
        gitaccess = GITAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/git/storageauthtest', ''))
        self.assertTrue(gitaccess.is_authentic())
        self.assertTrue(gitaccess.has_permission())

        gitaccess = GITAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/git/storageauthtest.git', ''))
        self.assertTrue(gitaccess.is_authentic())
        self.assertTrue(gitaccess.has_permission())

        # Simple write cases when having read access
        gitaccess = GITAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/git/storageauthtest.git', 'service=git-receive-pack&some=other'))
        self.assertTrue(gitaccess.is_authentic())
        self.assertFalse(gitaccess.has_permission())

        gitaccess = GITAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/git/storageauthtest.git', 'some=other&service=git-receive-pack'))
        self.assertTrue(gitaccess.is_authentic())
        self.assertFalse(gitaccess.has_permission())

        gitaccess = GITAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/git/storageauthtest.git/refs/jotain/git-receive-pack', ''))
        self.assertTrue(gitaccess.is_authentic())
        self.assertFalse(gitaccess.has_permission())

        # Kenny has write access to storageauthtest

        # Simple read cases when having write access
        gitaccess = GITAccessControl(DummyReq('kenny', 'ohmygod', 'GET', '/git/storageauthtest', ''))
        self.assertTrue(gitaccess.is_authentic())
        self.assertTrue(gitaccess.has_permission())

        gitaccess = GITAccessControl(DummyReq('kenny', 'ohmygod', 'GET', '/git/storageauthtest.git', ''))
        self.assertTrue(gitaccess.is_authentic())
        self.assertTrue(gitaccess.has_permission())

        # Simple write cases when having write access
        gitaccess = GITAccessControl(DummyReq('kenny', 'ohmygod', 'GET', '/git/storageauthtest.git', 'service=git-receive-pack&some=other'))
        self.assertTrue(gitaccess.is_authentic())
        self.assertTrue(gitaccess.has_permission())

        gitaccess = GITAccessControl(DummyReq('kenny', 'ohmygod', 'GET', '/git/storageauthtest.git', 'some=other&service=git-receive-pack'))
        self.assertTrue(gitaccess.is_authentic())
        self.assertTrue(gitaccess.has_permission())

        gitaccess = GITAccessControl(DummyReq('kenny', 'ohmygod', 'GET', '/git/storageauthtest.git/refs/jotain/git-receive-pack', ''))
        self.assertTrue(gitaccess.is_authentic())
        self.assertTrue(gitaccess.has_permission())
