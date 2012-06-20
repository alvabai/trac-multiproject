from multiproject.core.migration import MigrateBase, MigrateMgr


class AuthenticationMethodDatatype(MigrateBase):

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = "Change authentication method datatype from enum to varchar"

    def upgrade(self):
        if self.applied():
            print "            Migration already applied"
            return True

        procedures = [
""" ALTER TABLE authentication CHANGE method method VARCHAR(32) COLLATE utf8_bin NOT NULL
"""
]

        return self.manager.db_upgrade(procedures)

    def downgrade(self):
        if not self.applied():
            print "            Migration 20110906120000_authentication_method_datatype.py not applied"
            return False

        procedures = [
""" ALTER TABLE authentication CHANGE method method enum('LDAP','Ovi','Forum','LocalDB') COLLATE utf8_bin NOT NULL
"""
]

        return self.manager.db_downgrade(procedures)

    def applied(self):
        return self.manager.db_applied("DESC authentication", 1, 1, 'varchar(32)')

MigrateMgr.instance().add(AuthenticationMethodDatatype())
