# -*- coding: utf-8 -*-
"""
Migration updates published date according to the is_published_project,
i.e., does the anonymous user have VIEW permission.

After this migration, the projects.published field is NULL <=> the project is public
(if the public_anon_group is configured to be "Public viewers:VIEW").

"""
from multiproject.core.db import admin_query, cursors
from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.configuration import Configuration
conf = Configuration.instance()

class UserPermissionRename(MigrateBase):

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = ("Migration updates published date according to the is_published_project, \n"
                            "i.e., does the anonymous user have permissions described in public_anon_group.")
        self.pretend_to_be_not_applied = False

    def upgrade(self):
        if self.applied():
            print "Migration already applied".rjust(12)
            return True

        if len(conf.public_anon_group[1]) < 1:
            print "Migration cannot be applied."
            print "Migration cannot be applied, since the public_anon_group permissions are not set"
            return False
        perm_conditions = self._get_perm_conditions()

        queries = ["""
            UPDATE projects
            SET published = created
            WHERE ({0})
            AND projects.published is NULL
            """.format(' AND '.join(perm_conditions)),
            """
            UPDATE projects
            SET published = NULL
            WHERE (NOT {0})
            AND projects.published is not NULL
            """.format(' OR NOT '.join(perm_conditions))]

        res = self.manager.db_upgrade(queries)

        return res

    def downgrade(self):
        if not self.applied():
            print "Migration {0} not applied yet".format(__file__).rjust(12)
            return False

        print "Migration {0} cannot be really applied, but it should not be a problem.".format(__file__).rjust(12)
        self.pretend_to_be_not_applied = True

        return True

    def applied(self):
        """
        Check if column exists or not
        :returns: True if exists, otherwise False
        """

        if self.pretend_to_be_not_applied:
            return False
        count_false_published = 0
        count_false_private = 0
        with admin_query() as cursor:
            perm_conditions = self._get_perm_conditions()
            # Select count for public projects with null published date
            cursor.execute("""
            SELECT COUNT(projects.environment_name) FROM projects
            WHERE ({0})
            AND projects.published is NULL
            """.format(' AND '.join(perm_conditions)))
            count_false_private = int(cursor.fetchone()[0])
            # Select count for non-public projects with non-null published date
            cursor.execute("""
            SELECT COUNT(projects.environment_name) FROM projects
            WHERE (NOT {0})
            AND projects.published is not NULL
            """.format(' OR NOT '.join(perm_conditions)))
            count_false_published = int(cursor.fetchone()[0])

        return count_false_private + count_false_published == 0

    def _get_perm_conditions(self):
        perm_conditions = []

        for perm in conf.public_anon_group[1]:
            perm_conditions.append("""EXISTS (SELECT group.trac_environment_key FROM `group`
                INNER JOIN user_group ON user_group.group_key = group.group_id
                INNER JOIN user ON user.user_id = user_group.user_key
                INNER JOIN group_permission ON group_permission.group_key = group.group_id
                INNER JOIN action ON action.action_id = group_permission.permission_key
                WHERE group.trac_environment_key = projects.trac_environment_key
                AND user.username = 'anonymous'
                AND action.action_string = '{0}')""".format(perm))
        return perm_conditions

MigrateMgr.instance().add(UserPermissionRename())
