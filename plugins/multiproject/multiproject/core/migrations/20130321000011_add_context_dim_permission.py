# -*- coding: utf-8 -*-
"""
Migration sets VALID_TO to 2050 and inserts new context_dim
"""
from multiproject.core.configuration import Configuration
conf = Configuration.instance()
from multiproject.core.db import analytical_query
from multiproject.core.migration import MigrateBase, MigrateMgr


class AddContextDimForPermission(MigrateBase):

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
                UPDATE %s.context_dim
                SET VALID_TO = '2050-11-21 14:54:02'
                WHERE (context IN ('Admin Users', 'Admin Groups','Home permissions','Group templates'))
                """
        queries.append(query % (conf.db_analytical_schema_name))   

        query1 =""" 
                INSERT INTO %s.context_dim(context, environment_type, path_info, VALID_FROM, VALID_TO)
                VALUES ('Home permissions', 'home', '/admin/general/permissions', '2013-03-21 14:54:02', '2050-11-21 14:54:02')
                """
        queries.append(query1 % (conf.db_analytical_schema_name))  

        query2 =""" 
                INSERT INTO %s.context_dim(context, environment_type, path_info, VALID_FROM, VALID_TO)
                VALUES ('Project permissions', 'project', '/admin/general/permissions', '2013-03-21 14:54:02', '2050-11-21 14:54:02')
                """

        queries.append(query2 % (conf.db_analytical_schema_name))


        return self.manager.db_upgrade(queries)

    def downgrade(self):
        if not self.applied():
            print "Migration {0} not applied yet".format(__file__).rjust(12)
            return False

        queries = ["""
        DELETE FROM %s.context_dim
        WHERE context IN ("Project permissions","Home permissions");
        """ % conf.db_analytical_schema_name]

        return self.manager.db_downgrade(queries)

    def applied(self):

        with analytical_query() as cursor:
            cursor.execute('''
                SELECT COUNT(*) AS count FROM %s.context_dim
                WHERE (context IN ('Project permissions','Home permissions','Admin Users','Admin Groups', 'Group templates'))
            ''' % conf.db_analytical_schema_name)
            row = cursor.fetchone()
            if row[0] == 6:
                return True

        return False

MigrateMgr.instance().add(AddContextDimForPermission())
