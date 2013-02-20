# -*- coding: utf-8 -*-
import MySQLdb
from multiproject.core.users import MySqlUserStore
from multiproject.core.stubs.DatabaseStub import DatabaseStub
from multiproject.core.stubs.UserStoreStub import UserStoreStub
import multiproject.core.configuration

dbStub = DatabaseStub()
userstoreStub = UserStoreStub()

conf = multiproject.core.configuration.Configuration.instance()
multiproject.core.configuration.Configuration.config_file = '/etc/trac/cqde.test.ini'
conf.refresh()


def stub_getUserStore(self):
    if conf._use_test_db:
        return MySqlUserStore()
    else:
        return userstoreStub


def stub_getAuthenticationStore(self):
    return userstoreStub


def stub_getAdminDbConnection(self):
    if conf._use_test_db:
        return MySQLdb.connect(host=self.db_host,
                               user=self.db_user,
                               passwd=self.db_password,
                               db=self.db_admin_schema_name)
    else:
        dbStub.closed = False
        return dbStub


def stub_getDbConnection(self, dbname = None):
    if conf._use_test_db:
        if dbname is None:
            return MySQLdb.connect(host=self.db_host,
                                   user=self.db_user,
                                   passwd=self.db_password,
                                   db='')
        else:
            return MySQLdb.connect(host=self.db_host,
                                   user=self.db_user,
                                   passwd=self.db_password,
                                   db=dbname)
    else:
        dbStub.closed = False
        return dbStub


def stub_getVersionControlType(self, projectname):
    return 'svn'


def use_test_db(self, value = True):
    conf._use_test_db = value


conf.global_conf_path = "/tmp/conffi.ini"

# Augment configuration with a method for setting which db to use
multiproject.core.configuration.Configuration.use_test_db = use_test_db

# Stub out some methods
multiproject.core.configuration.Configuration.getUserStore = stub_getUserStore
multiproject.core.configuration.Configuration.getAuthenticationStore = stub_getAuthenticationStore
multiproject.core.configuration.Configuration.getAdminDbConnection = stub_getAdminDbConnection
multiproject.core.configuration.Configuration.getDbConnection = stub_getDbConnection

multiproject.core.configuration.Configuration.getVersionControlType = stub_getVersionControlType

# Replace some configuration variables, just in case, to prevent messing up the real system
conf.use_test_db(False)
