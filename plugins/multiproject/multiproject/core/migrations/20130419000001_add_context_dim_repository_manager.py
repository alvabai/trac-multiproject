# -*- coding: utf-8 -*-
"""
Add new row to context dim for repository manager
"""
from multiproject.core.configuration import conf
from multiproject.core.db import analytical_query
from multiproject.core.migration import MigrateBase, MigrateMgr

class AddContextDimForRepositoryManager(MigrateBase):

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
                INSERT INTO %s.context_dim(context, environment_type, path_info, VALID_FROM, VALID_TO)
                VALUES ('Admin Project VCM', 'project', '/admin/general/vcm', ' 2011-01-27 09:08:05', '2050-11-21 14:54:02')
                """
        queries.append(query % (conf.db_analytical_schema_name))   


        queries.append(query2 % (conf.db_analytical_schema_name))


        return self.manager.db_upgrade(queries)

    def downgrade(self):
        if not self.applied():
            print "Migration {0} not applied yet".format(__file__).rjust(12)
            return False

        queries = ["""
        DELETE FROM %s.context_dim
        WHERE context = "Admin Project VCM");
        """ % conf.db_analytical_schema_name]

        return self.manager.db_downgrade(queries)

    def applied(self):

        with analytical_query() as cursor:
            cursor.execute('''
                SELECT COUNT(*) AS count FROM %s.context_dim
                WHERE context = 'Admin Project VCM'
            ''' % conf.db_analytical_schema_name)
            row = cursor.fetchone()
            if row[0] == 1:
                return True

        return False

MigrateMgr.instance().add(AddContextDimForPermission())