#!/usr/bin/python
# coding: utf-8

import unittest

import util
from util import sanitize_html

class test_sanitize_html(unittest.TestCase):

    def setUp(self):
        pass

    def test_empty(self):
        res = sanitize_html(None)
        self.assertEqual(res, "")


if __name__ == '__main__':
    unittest.main()

# vim: sw=4

