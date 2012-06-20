from multiproject.core.stubs import DummyReq
from ...ConfigurationStub import conf
from multiproject.core.test.cqdetestcase import CQDETestCase
from multiproject.core.auth.hg_access import MercurialAccessControl

class HgAccessControlTestCase(CQDETestCase):
    def tearDown(self):
        conf.use_test_db(False)

    def testInit(self):
        # cmd must be set correctly at init time
        pass

    def testIsProtocolRequest(self):
        # No command => not protocol request
        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest', ''))
        self.assertFalse(hgaccess.is_protocol_request())

        # Not protocol command => not protocol request
        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest', 'cmd=log'))
        self.assertFalse(hgaccess.is_protocol_request())

        # Path continues after project name => not protocol request
        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest/branches', 'cmd=log'))
        self.assertFalse(hgaccess.is_protocol_request())

        # Ending slash in the request and wrong command, => not protocol request
        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest/', 'cmd=log'))
        self.assertFalse(hgaccess.is_protocol_request())

        # Ending slash in the request but no path, => protocol request
        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest/', 'cmd=branches'))
        self.assertTrue(hgaccess.is_protocol_request())

        # Valid cmd, valid path => protocol request
        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest', 'cmd=branches&foo=bar'))
        self.assertTrue(hgaccess.is_protocol_request())

        # Valid cmd, valid path => protocol request
        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest', 'foo=bar&cmd=branches'))
        self.assertTrue(hgaccess.is_protocol_request())

    def testIsRead(self):
        # Should be read in case that
        #    cmd not in perms or perms[cmd] != 'push'
        # Is not read if
        #    cmd in perms and perms[cmd] = 'push' == not ( is_read )
        #
        # perms = {
        #    'changegroup': 'pull',
        #    'changegroupsubset': 'pull',
        #    'stream_out': 'pull',
        #    'listkeys': 'pull',
        #    'unbundle': 'push',
        #    'pushkey': 'push',
        # }
        conf.use_test_db(False)

        # Simple read cases
        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest', 'cmd=stream_out'))
        self.assertTrue(hgaccess.is_read())

        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest', 'cmd=changegroupsubset'))
        self.assertTrue(hgaccess.is_read())

        # Simple write cases
        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest', 'cmd=unbundle'))
        self.assertFalse(hgaccess.is_read())

        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest', 'cmd=pushkey'))
        self.assertFalse(hgaccess.is_read())

        # What if cmd is given twice? One with read and one with write? Someone tries to disguise write access as read access
        # In this case it should test against the strongest command
        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest', 'cmd=stream_out&cmd=pushkey'))
        self.assertFalse(hgaccess.is_read())

        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest', 'cmd=pushkey&cmd=stream_out'))
        self.assertFalse(hgaccess.is_read())

    def testAccess(self):
        conf.use_test_db(True)
        self.load_fixtures()

        # Cartman has read access to storageauthtest

        # Simple read cases when having read access
        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest', 'cmd=stream_out'))
        self.assertTrue(hgaccess.has_permission())

        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest', 'cmd=changegroupsubset'))
        self.assertTrue(hgaccess.has_permission())

        # Simple write cases when having read access
        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest', 'cmd=unbundle'))
        self.assertFalse(hgaccess.has_permission())

        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest', 'cmd=pushkey'))
        self.assertFalse(hgaccess.has_permission())

        hgaccess = MercurialAccessControl(DummyReq('cartman', 'cartmans_pw', 'GET', '/hg/storageauthtest', 'cmd=stream_out&cmd=pushkey'))
        self.assertFalse(hgaccess.has_permission())

        # Kenny has write access to storageauthtest

        # Simple read cases when having write access
        hgaccess = MercurialAccessControl(DummyReq('kenny', 'ohmygod', 'GET', '/hg/storageauthtest', 'cmd=stream_out'))
        self.assertTrue(hgaccess.has_permission())

        hgaccess = MercurialAccessControl(DummyReq('kenny', 'ohmygod', 'GET', '/hg/storageauthtest', 'cmd=changegroupsubset'))
        self.assertTrue(hgaccess.has_permission())

        # Simple write cases when having write access
        hgaccess = MercurialAccessControl(DummyReq('kenny', 'ohmygod', 'GET', '/hg/storageauthtest', 'cmd=unbundle'))
        self.assertTrue(hgaccess.has_permission())

        hgaccess = MercurialAccessControl(DummyReq('kenny', 'ohmygod', 'GET', '/hg/storageauthtest', 'cmd=pushkey'))
        self.assertTrue(hgaccess.has_permission())

        hgaccess = MercurialAccessControl(DummyReq('kenny', 'ohmygod', 'GET', '/hg/storageauthtest', 'cmd=stream_out&cmd=pushkey'))
        self.assertFalse(hgaccess.has_permission())
