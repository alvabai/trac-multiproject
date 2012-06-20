# -*- coding: utf-8 -*-
from multiproject.core.test.cqdetestcase import CQDETestCase
import multiproject.core.auth.auth


class AuthenticationTestCase(CQDETestCase):

    def setUp(self):
        self.log = self

    def tearDown(self):
        self.log = None

    def test_is_allowed_host(self):
        g = multiproject.core.auth.auth.Authentication()
        self.assertFalse(g._is_allowed_host('something'))
        self.assertTrue(g._is_allowed_host('it.local'))
        self.assertTrue(g._is_allowed_host('something.it.local'))
        self.assertFalse(g._is_allowed_host('it.local.something'))

    # dummy log.debug
    def debug(self, msg):
        pass
