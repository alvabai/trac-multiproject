#!/usr/bin/env python
# coding: utf-8

import unittest2 as unittest
import htlib

class TestGetSessionDict(unittest.TestCase):

    def testOneString(self):
        ret = htlib.headers_to_dict('foo_session=890az; lkj=324; expires=Sun, 07 Apr 2013 08:04:33; Path=/', key="foo")

        self.assertEqual(ret, {'foo_session': '890az'})

    def testSimpleList(self):
        ret = htlib.headers_to_dict(['foo_session=890az; lkj=324; expires=Sun, 07 Apr 2013 08:04:33; Path=/'], key="foo")

        self.assertEqual(ret, {'foo_session': '890az'})


    def testList(self):
        ret = htlib.headers_to_dict(['foo_session=890az; lkj=324', 
                                    'bar=jlöj90u; foo_auth=4de33' ], key="foo")

        self.assertEqual(ret, {'foo_session': '890az', 'foo_auth': '4de33'})


class TestGetCookieHeader(unittest.TestCase):

    def testSimple(self):
        data = {'foo_auth': '123', 'foo_token': 'asdf'}
        ret = htlib.get_cookie_header(data)
        self.assertEqual(ret, 'foo_auth=123; foo_token=asdf')



if __name__ == "__main__":
    unittest.main()

# vim: sw=4

