# -*- coding: utf-8 -*-
"""
Migration adds project watchers event types
"""
from multiproject.core.configuration import Configuration
conf = Configuration.instance()
from multiproject.core.db import analytical_query
from multiproject.core.migration import MigrateBase, MigrateMgr


class ProjectWatchEventTypes(MigrateBase):

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = __doc__
        self.actions = {
            'project_watchers':'update',
        }

    def upgrade(self):
        if self.applied():
            print "Migration already applied".rjust(12)
            return True

        queries = []
        query = """
        INSERT INTO %s.event_dim (action_name, CRUD, context, VALID_FROM, VALID_TO)
        VALUES ('%s', '%s', 'Project', TIMESTAMP(NOW()), NULL)
        """

        for action, crud in self.actions.items():
            queries.append(query % (conf.db_analytical_schema_name, action, crud.title()))

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

        for action in self.actions.keys():
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
        return not all([(action not in action_names) for action in self.actions.keys()])

MigrateMgr.instance().add(ProjectWatchEventTypes())
