#!/usr/bin/python
# coding: utf-8

import unittest

# TODO kludge: move path setting to a runner script
import sys
sys.path.append('../../..')

import util
from util import sanitize_html

class Test_sanitize_html(unittest.TestCase):
    """Test util.util.sanitize_html"""

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

    def test_removing_tags(self):
        """Don't trim spaces""" 
        res = sanitize_html(' <foo>my text here!</foo>')
        self.assertEqual(res, " ")

    def test_removing_element(self):
        """Remove html elements"""
        html = "playnice<something>nasty<!-- javascript --></something>"
        res = sanitize_html(html)
        self.assertEqual(res, "playnice")

    def test_remove_lone_tags(self):
        """One-tag -elements should be removed."""
        html = "<foo/>Leave me"""
        res = sanitize_html(html)
        self.assertEqual(res, "Leave me")

    def test_remove_script(self):
        """Remove javascript."""
        html = """<p onClick="alert('Hello');">foo</p>"""
        res = sanitize_html(html)
        self.assertEqual(res, "<p>foo</p>")


if __name__ == '__main__':
    unittest.main()

# vim: sw=4

