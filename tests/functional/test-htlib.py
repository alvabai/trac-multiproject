#!/usr/bin/env python
# coding: utf-8

import unittest2 as unittest
import htlib

class TestGetSessionDict(unittest.TestCase):

    def testFoo(self):
        ret = htlib.get_session_dict('foo_session=890az; \
                    foo_auth=4de33; \
                    foo_form_token=1234; expires=Sun, 07 Apr 2013 08:04:33; \
                    Path=/', key="foo")

        self.assertEqual(ret, {'foo_session': '890az', 
                           'foo_auth': '4de33', 
                           'foo_form_token': '1234'}
                    )

if __name__ == "__main__":
    unittest.main()

# vim: sw=4

