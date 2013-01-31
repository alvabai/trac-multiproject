# -*- coding: utf-8 -*-
from multiproject.core.test.cqdetestcase import CQDETestCase
import multiproject.core.auth.auth


class AuthenticationTestCase(CQDETestCase):

    def setUp(self):
        self.log = self

    def tearDown(self):
        self.log = None

    # dummy log.debug
    def debug(self, msg):
        pass
