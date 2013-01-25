import unittest2 as unittest

from core.dbTest import *

class TestDBModule(unittest.TestCase):
    def setUp(self):
        pass

    def test_admin_query_called(self):
        admin_query_called = False
        admin_query_called = admin_query()
        self.assertTrue(admin_query_called)

if __name__ == "__main__":

    unittest.main()