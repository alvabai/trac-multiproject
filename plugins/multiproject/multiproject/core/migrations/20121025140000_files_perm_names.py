from multiproject.core.db import admin_query, cursors
from multiproject.core.migration import MigrateBase, MigrateMgr


class RenameFilesPerms(MigrateBase):

    # pairs of new name, old name
    renames = (('FILES_VIEW', 'WEBDAV_VIEW'), ('FILES_ADMIN', 'WEBDAV'),
               ('FILES_DOWNLOADS_VIEW', 'DOWNLOADS_VIEW'), ('FILES_DOWNLOADS_ADMIN', 'DOWNLOADS_ADMIN'))

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = self.__doc__
        self.pretend_to_be_not_applied = False

    def applied(self):
        with admin_query() as cursor:
            cursor.execute("SELECT * FROM action WHERE action_string='FILES_DOWNLOADS_VIEW'")
            result = cursor.fetchone() is not None
            if not result:
                cursor.execute("SELECT * FROM action WHERE action_string='WEBDAV'")
                result = cursor.fetchone() is None
            return result

    def upgrade(self):
        if self.applied():
            return
        queries = []
        for new, old in self.renames:
            # delete incase someone has added the new permission name to database (eg. while testing)
            queries.append("DELETE FROM `action` WHERE `action_string` = '%s'" % new)
            queries.append("UPDATE `action` SET `action_string`='%s' WHERE `action_string`='%s'" % (new, old))

        # delete permission
        queries.append("DELETE FROM `action` WHERE `action_string` = 'DOWNLOADS_ADD'")
        return self.manager.db_upgrade(queries)

    def downgrade(self):
        queries = []
        for old, new in self.renames:
            # delete incase someone has added the new permission name to database (eg. while testing)
            queries.append("DELETE FROM `action` WHERE `action_string` = '%s'" % new)
            queries.append("UPDATE `action` SET `action_string`='%s' WHERE `action_string`='%s'" % (new, old))
        return self.manager.db_upgrade(queries)

MigrateMgr.instance().add(RenameFilesPerms())
