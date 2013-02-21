# -*- coding: utf-8 -*-
import trac.core

import multiproject.common.users.icon
from multiproject.tests.ConfigurationStub import conf, dbStub
from multiproject.core.test.cqdetestcase import CQDETestCase

class DummyReq(object):
    def __init__(self):
        self.args = {
            'username': 'user',
            'user_id': 'id'
        }
        self.response = 0
        self.content = None

    def send_response(self, response):
        self.response = response

    def send_header(self, header, value):
        pass

    def end_headers(self):
        pass

    def write(self, content):
        self.content = content

class IconRendererTestCase(CQDETestCase):

    def setUp(self):
        conf.use_test_db(False)
        dbStub.addResult([[1, "data", "image/gif"]])
        self.cm = trac.core.ComponentManager()
        self.req = DummyReq()

    def tearDown(self):
        dbStub.reset()
        self.cm = None
        self.req = None

    def test_process_request(self):
        i = multiproject.common.users.icon.IconRenderer(self.cm)
        i.process_request(self.req)
        self.assertEquals(self.req.response, 200)
        self.assertEquals(self.req.content, 'data')
        self.assertTrue(dbStub.closed)

    def test_process_request_error(self):
        dbStub.setExceptions(True)
        i = multiproject.common.users.icon.IconRenderer(self.cm)
        i.process_request(self.req)
        self.assertEquals(self.req.content, '')
        self.assertTrue(dbStub.closed)
