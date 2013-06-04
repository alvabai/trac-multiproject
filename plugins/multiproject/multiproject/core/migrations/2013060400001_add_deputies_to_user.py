# -*- coding: utf-8 -*-
"""
Add new column to user for deputies
"""
from multiproject.core.configuration import conf
from multiproject.core.db import analytical_query
from multiproject.core.migration import MigrateBase, MigrateMgr

class AddDeputiesForUsers(MigrateBase):

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = __doc__

    def upgrade(self):
        if self.applied():
            print "Migration already applied".rjust(12)
            return True

        queries = []
        query = """
                ALTER trac_admin.user ALTER TABLE user ADD deputies TEXT;
                """
        queries.append(query % (conf.db_analytical_schema_name))


        return self.manager.db_upgrade(queries)

    def downgrade(self):
        if not self.applied():
            print "Migration {0} not applied yet".format(__file__).rjust(12)
            return False

        queries = ["""
            ALTER TABLE trac_admin.user DROP deputies
        """]

        return self.manager.db_downgrade(queries)

    def applied(self):

        with admin_query() as cursor:
            cursor.execute('''
                SELECT COLUMN_NAME FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = 'trac_admin' 
                    AND TABLE_NAME = 'user' 
                    AND COLUMN_NAME = 'deputies';
            ''')
            row_num = int(cursor.rowcount)
            if row_num == 1:
                return True

        return False

MigrateMgr.instance().add(AddDeputiesForUsers())