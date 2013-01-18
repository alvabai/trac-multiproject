#!/usr/bin/python
# coding: utf-8

import unittest

# TODO kludge: move path setting to a runner script
import sys
sys.path.append('../../..')

import util
from util import sanitize_html

class Test_sanitize_html(unittest.TestCase):

    def setUp(self):
        pass

    def test_None(self):
        """With None return empty string"""
        res = sanitize_html(None)
        self.assertEqual(res, "")

    def test_empty(self):
        """Without input return empty string"""
        res = sanitize_html("")
        self.assertEqual(res, "")




if __name__ == '__main__':
    unittest.main()

# vim: sw=4

