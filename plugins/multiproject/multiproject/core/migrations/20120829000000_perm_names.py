from multiproject.core.db import admin_query, cursors
from multiproject.core.migration import MigrateBase, MigrateMgr


class RenamePerms(MigrateBase):

    # pairs of new name, old name
    renames = (('PROJECT_VIEW', 'SUMMARY_VIEW'), ('PROJECT_PRIVATE_VIEW', 'PRIVATE_SUMMARY_VIEW'),
               ('PROJECT_CREATE', 'CREATE_PROJECT'), ('MEMBERSHIP_REQUEST_CREATE', 'ALLOW_REQUEST_MEMBERSHIP'))

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = self.__doc__
        self.pretend_to_be_not_applied = False

    def applied(self):
        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM action WHERE action_string='SUMMARY_VIEW'")
            return cursor.fetchone() is None

    def upgrade(self):
        if self.applied():
            return
        queries = []
        for new, old in self.renames:
            # delete incase someone has added the new permission name to database (eg. while testing)
            queries.append("DELETE FROM `action` WHERE `action_string` = '%s'" % new)
            queries.append("UPDATE `action` SET `action_string`='%s' WHERE `action_string`='%s'" % (new, old))

        # delete permission
        queries.append("DELETE FROM `action` WHERE `action_string` = 'LIST_ALL_PROJECTS'")
        return self.manager.db_upgrade(queries)

    def downgrade(self):
        queries = []
        for old, new in self.renames:
            # delete incase someone has added the new permission name to database (eg. while testing)
            queries.append("DELETE FROM `action` WHERE `action_string` = '%s'" % new)
            queries.append("UPDATE `action` SET `action_string`='%s' WHERE `action_string`='%s'" % (new, old))
        return self.manager.db_upgrade(queries)

MigrateMgr.instance().add(RenamePerms())
