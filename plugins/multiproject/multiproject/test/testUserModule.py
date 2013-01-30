import unittest2 as unittest

from core.userTest import *

class TestUserModule(unittest.TestCase):
    def setUp(self):
        pass

    def test_username_with_tero_test_should_have_user(self):
        user_store = get_userstore()
        user = user_store.getUser("tero.test")
        self.assertEqual(user.id, 1)

    def test_username_with_other_than_tero_test_should_not_have_user(self):
        user_store = get_userstore()
        user = user_store.getUser("mikko.mallikas")
        self.assertIsNone(user)


if __name__ == "__main__":

    unittest.main()