# -*- coding: utf-8 -*-
import trac.core
from multiproject.tests.ConfigurationStub import conf
from multiproject.core.test.cqdetestcase import CQDETestCase


class DummyArgs(dict):
    def getlist(self, param):
        return self[param]


class DummyReq(object):
    def __init__(self):
        self.method = 'POST'
        self.href = trac.web.Href('/tmp') #@UndefinedVariable
        self.args = DummyArgs()
        self.args['group'] = None
        self.chrome = DummyArgs()
        self.chrome['warnings'] = []
        self.chrome['notices'] = []

        class DummyPerm(object):
            def require(self, rights):
                pass

        self.perm = DummyPerm()
