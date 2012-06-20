# -*- coding: utf-8 -*-
"""
This module tests the functionality of the :mod:`multiproject.common.admin.backup`
"""
__author__ = 'jumuston'

import os

import trac.core
from trac.test import EnvironmentStub
from trac.tests.functional import FunctionalTestCaseSetup, FunctionalTwillTestCaseSetup, FunctionalTestSuite

from multiproject.common.admin.backup import BackupRestoreModule
from multiproject.tests.ConfigurationStub import conf


class BackupRestoreModuleTestCase(FunctionalTestCaseSetup):
    """

    """
    def __setUp(self):
        """Setting up the test case"""
        super(BackupRestoreModuleTestCase, self).setUp()
        
        env = self._testenv.get_trac_environment()
        # raises TracError if backup fails
        backup_file = env.backup()
        
        self.assertTrue(os.path.exists(backup_file), 'Backup file was not created.')
        self.assertNotEqual(os.path.getsize(backup_file), 0, 'Backup file is zero length.')
        
        self.env = EnvironmentStub()
        self.cm = trac.core.ComponentManager()
        conf.use_test_db(True)

    def runTest(self):
        """Testing backup"""
        env = self._testenv.get_trac_environment()

        # raises TracError if backup fails
        backup_file = env.backup()
        self.assertTrue(os.path.exists(backup_file), 'Backup file was not created.')
        self.assertNotEqual(os.path.getsize(backup_file), 0, 'Backup file is zero length.')


    def tearDown(self):
        self.cm = None
        conf.use_test_db(False)

    def test_add_and_remove_user_from_group(self):
        print 'testing'

        b = BackupRestoreModule(self.cm)
        cnx = b._backup()

        print dir(cnx)


class TestBasicSettings(FunctionalTwillTestCaseSetup):
    def runTest(self):
        """Check basic settings."""
        self._tester.go_to_admin()
        tc.formvalue('modbasic', 'url', 'https://my.example.com/something')
        tc.submit()
        tc.find('https://my.example.com/something')
