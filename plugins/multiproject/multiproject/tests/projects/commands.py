# -*- coding: utf-8 -*-
from multiproject.common.projects.project import Project
from multiproject.core.permissions import CQDEUserGroupStore
from multiproject.core.users import User
import multiproject.common.projects.commands
from multiproject.tests.ConfigurationStub import dbStub, conf
from multiproject.core.test.cqdetestcase import CQDETestCase

class DummyCommand(multiproject.common.projects.commands.Command):

    def do(self):
        return True

    def undo(self):
        return True

class CommanderTestCase(CQDETestCase):

    def setUp(self):
        self.command1 = DummyCommand()
        self.command2 = DummyCommand()

    def tearDown(self):
        self.command1 = None
        self.command2 = None

    def test_run_single(self):
        c = multiproject.common.projects.commands.Commander()
        self.assertTrue(c.run(self.command1))
        self.assertTrue(c.rollback())
        self.assertEquals(c.rollback(), None)

    def test_run_multiple(self):
        c = multiproject.common.projects.commands.Commander()
        self.assertTrue(c.run(self.command1))
        self.assertTrue(c.run(self.command2))
        self.assertEquals(c.rollallback(), None)
        self.assertEquals(c.rollback(), None)

class CreateTracDatabaseTestCase(CQDETestCase):

    def setUp(self):
        self.projectObj = Project(None, 'testi', 'Long name', 'Desc', 1, None)
        dbStub.addResult([])

    def tearDown(self):
        dbStub.reset()

    def test_do(self):
        command = multiproject.common.projects.commands.CreateTracDatabase(self.projectObj)
        self.assertFalse(command.success)
        self.assertTrue(command.do())
        self.assertTrue(command.success)
        self.assertTrue(dbStub.cursors[0].query.lower().startswith("create database `testi`"))
        self.assertTrue(dbStub.closed)

    def test_do_error(self):
        dbStub.setExceptions(True)
        command = multiproject.common.projects.commands.CreateTracDatabase(self.projectObj)
        self.assertFalse(command.do())
        self.assertFalse(command.success)
        self.assertTrue(dbStub.closed)

    def test_undo(self):
        command = multiproject.common.projects.commands.CreateTracDatabase(self.projectObj)
        command.success = True
        self.assertTrue(command.undo())
        self.assertTrue(dbStub.cursors[0].query.lower().startswith("drop database `testi`"))
        self.assertTrue(dbStub.closed)

    def test_undo_error(self):
        dbStub.setExceptions(True)
        command = multiproject.common.projects.commands.CreateTracDatabase(self.projectObj)
        command.success = True
        self.assertFalse(command.undo())
        self.assertTrue(dbStub.closed)

class ListUpProjectTestCase(CQDETestCase):

    def setUp(self):
        self.projectObj = Project(None, 'short_name', 'Long name', 'Desc', 1, None)
        dbStub.addResult([])

    def tearDown(self):
        dbStub.reset()

    def test_do(self):
        dbStub.addResult([])
        command = multiproject.common.projects.commands.ListUpProject(self.projectObj)
        self.assertFalse(command.success)
        self.assertTrue(command.do())
        self.assertTrue(command.success)
        self.assertTrue(dbStub.closed)

    def test_undo(self):
        command = multiproject.common.projects.commands.ListUpProject(self.projectObj)
        command.success = True
        self.assertTrue(command.undo() == True)
        self.assertTrue(dbStub.closed)

    def test_undo_error(self):
        dbStub.setExceptions(True)
        command = multiproject.common.projects.commands.ListUpProject(self.projectObj)
        command.success = True
        self.assertFalse(command.undo())
        self.assertTrue(dbStub.closed)

class SetPermissionsTestCase(CQDETestCase):

    def setUp(self):
        userObj = User()
        userObj.id = 30
        userObj.username = 'testuser'

        self.projectObj = Project(24, 'storageauthtest', 'Storage auth testing', 'Desc',
                                  userObj.id, None, author = userObj)
        conf.use_test_db(True)
        self.load_fixtures()
        self.store = CQDEUserGroupStore(self.projectObj.id)
        self.store.remove_group('Owners')
        self.store.remove_group('Public contributors')
        self.store.remove_group('Public viewers')

    def tearDown(self):
        conf.use_test_db(False)

    # TODO
    #def test_do(self):
        #command = multiproject.common.projects.commands.SetPermissions(self.projectObj)
        #self.assertTrue(command.do())

        #gid = self.store.get_group_id('Owners')

        #self.assertNotEquals(gid, None)

        #ugs = self.store.get_all_user_groups()
        #self.assertIn(('testuser', 'Owners'), ugs)

        #gps = self.store.get_all_group_permissions()
        #self.assertIn(('Owners', 'TRAC_ADMIN'), gps)

        ## Clean up
        #self.store.remove_group('Owners')

    def test_undo(self):
        conf.use_test_db(True)
        self.load_fixtures()
        # Prepare
        command = multiproject.common.projects.commands.SetPermissions(self.projectObj)
        # Try undo
        self.assertTrue(command.undo())
