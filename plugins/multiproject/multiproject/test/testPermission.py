# -*- coding: utf-8 -*-

import unittest2 as unittest

from core.permissionTest import *

class TestPermission(unittest.TestCase):
    def setUp(self):
        pass

    def test_remove_user_with_tero_test_as_username_and_project1_as_group_name_should_return_true(self):
        user_group_store = CQDEUserGroupStoreStub()
        check_val = user_group_store.remove_user_from_group("tero.test", "project1")
        self.assertTrue(check_val)

    def test_remove_user_with_tero_test_as_username_and_project2_as_group_name_should_return_false(self):
        user_group_store = CQDEUserGroupStoreStub()
        check_val = user_group_store.remove_user_from_group("tero.test", "project2")
        self.assertFalse(check_val)

    def test_remove_use_with_mikko_mallikas_as_username_and_project3_as_group_name_should_return_false(self):
        user_group_store = CQDEUserGroupStoreStub()
        check_val = user_group_store.remove_user_from_group("mikko.mallikas", "project3")
        self.assertFalse(check_val)