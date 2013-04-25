#!/usr/bin/env python
# coding: utf-8

import sys
import os
import unittest2 as unittest

from mock import MagicMock
from mock import patch

sys.path.append(
    os.path.normpath(
        os.path.join( os.path.abspath(os.path.dirname(__file__)), "..")
    )
)

import db

class MyConfTest(unittest.TestCase):
    # patch name has to match the import
    @patch('multiproject.core.configuration.Configuration')
    def test_get_db_connect(self, mock):

        db._get_pool = MagicMock()
        # note, setting return value has to have exactly the same format with the
        # method call. So e.g a.b.return_value doesn't work if call is a().b().
        db._get_pool().connect.return_value = "the result"
        result = db.get_connection()
        self.assertEquals(result, 'the result')


if __name__ == "__main__":
    unittest.main()

# vim: sw=4

