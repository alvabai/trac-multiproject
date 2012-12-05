# -*- coding: utf-8 -*-
"""
Migration adds files related copy event type
"""
from multiproject.core.configuration import conf
from multiproject.core.db import analytical_query
from multiproject.core.migration import MigrateBase, MigrateMgr


class FilesCopyEvent(MigrateBase):
    """
    Migration adds files related copy event type
    """

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = __doc__
        self.actions = [
                ('file_copied', 'create', 'Files'),
                ('release_copied', 'create', 'Releases'),
                ('release_moved', 'update', 'Releases'),
                ('release_deleted', 'delete', 'Releases'),
            ]

    def upgrade(self):
        if self.applied():
            print "Migration already applied".rjust(12)
            return True

        queries = []
        query = """
        INSERT INTO %s.event_dim (action_name, CRUD, context, VALID_FROM, VALID_TO)
        VALUES ('%s', '%s', '%s', TIMESTAMP(NOW()), NULL)
        """

        for action, crud, context in self.actions:
            queries.append(query % (conf.db_analytical_schema_name, action, crud.title(), context))

        return self.manager.db_upgrade(queries)

    def downgrade(self):
        if not self.applied():
            print "Migration {0} not applied yet".format(__file__).rjust(12)
            return False

        queries = []
        query = """
        DELETE FROM %s.event_dim
        WHERE action_name = '%s'
        """

        for  action, crud, context  in self.actions:
            queries.append(query % (conf.db_analytical_schema_name, action))

        return self.manager.db_downgrade(queries)

    def applied(self):
        """
        Check if column exists or not
        :returns: True if exists, otherwise False
        """
        action_names = []

        with analytical_query() as cursor:
            cursor.execute('SELECT action_name FROM %s.event_dim' % conf.db_analytical_schema_name)
            action_names = [row[0] for row in cursor]

        # Check if all actions can be found from event_dim
        return not all([(action not in action_names) for  action, crud, context in self.actions])

MigrateMgr.instance().add(FilesCopyEvent())


