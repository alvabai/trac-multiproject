"""
Uses database for analytics json data
"""
from multiproject.core.configuration import Configuration
conf = Configuration.instance()
from multiproject.core.db import analytical_query
from multiproject.core.migration import MigrateBase, MigrateMgr


class AnalyticsJSON(MigrateBase):

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = __doc__

    def upgrade(self):
        if self.applied():
            print "Migration already applied".rjust(12)
            return True

        queries = ["""
        CREATE TABLE %s.data_queue (
            `id` INT(10) NOT NULL AUTO_INCREMENT,
            `data` LONGTEXT NULL,
            PRIMARY KEY (`id`)
        )
        """ % conf.db_analytical_schema_name]
        return self.manager.db_upgrade(queries)

    def downgrade(self):
        if not self.applied():
            print "Migration {0} not applied yet".format(__file__).rjust(12)
            return False

        queries = ["""
        DROP TABLE %s.data_queue
        """ % conf.db_analytical_schema_name]
        return self.manager.db_downgrade(queries)

    def applied(self):
        with analytical_query() as cursor:
            cursor.execute('SHOW TABLES LIKE "data_queue"')
            for row in cursor:
                return True
        return False

MigrateMgr.instance().add(AnalyticsJSON())
