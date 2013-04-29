# -*- coding: utf-8 -*-
"""
Migration to add (project_id, status) index into project download table.
"""

from multiproject.core.db import admin_query
from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.configuration import Configuration
conf = Configuration.instance()


class DownloadStatusIndex(MigrateBase):
    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = self.__doc__

    def upgrade(self):
        if self.applied():
            print "project download status index is already in database"
            return True

        queries = [
            '''
            CREATE INDEX download_status_idx ON `project_download`
            (project_id, status, download_path(255));
            ''']

        return self.manager.db_upgrade(queries)

    def downgrade(self):
        if not self.applied():
            print ""
            return True

        queries = ['DROP INDEX download_status_idx ON `project_download`']
        return self.manager.db_downgrade(queries)

    def applied(self):
        with admin_query() as cursor:
            cursor.execute('''
                SELECT COUNT(*) FROM information_schema.statistics
                WHERE table_schema = %s
                AND table_name = 'project_download'
                AND index_name = 'download_status_idx';
            ''', conf.db_admin_schema_name)
            row = cursor.fetchone()
            if row[0] == 0:
                return False

        return True


MigrateMgr.instance().add(DownloadStatusIndex())
