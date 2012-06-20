# -*- coding: utf-8 -*-
"""
Migration updates passwords of the users which are not local:

- Updates passwords hashes to 'invalidNonLocalUserPwHash' for users
  with authentication key other than that of local.

"""
from multiproject.core.db import admin_query, cursors, safe_int
from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.permissions import CQDEAuthenticationStore


class NonLocalUsersPasswordHashInvalidating(MigrateBase):

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = __doc__
        self._pretend_not_applied = False

    def upgrade(self):
        if self.applied():
            print "Migration already applied".rjust(12)
            return True

        auth_store = CQDEAuthenticationStore.instance()
        id = auth_store.get_authentication_id(auth_store.LOCAL)
        if not id:
            print "Error: local authentication id not found: name is %s" % auth_store.LOCAL
            return False

        queries = ["""
        UPDATE `user`
           SET SHA1_PW = 'invalidNonLocalUserPwHash'
         WHERE authentication_key <> %s
        """ % safe_int(id)]

        return self.manager.db_upgrade(queries)

    def downgrade(self):
        print "Error: This migration cannot be really downgraded, but it should not be an issue"
        self._pretend_not_applied = True
        return True

    def applied(self):
        """
        Check if column exists or not
        :returns: True if exists, otherwise False
        """
        if self._pretend_not_applied:
            return False

        count = 0
        auth_store = CQDEAuthenticationStore.instance()
        id = auth_store.get_authentication_id(auth_store.LOCAL)
        with admin_query() as cursor:
            cursor.execute("""
            SELECT COUNT(*) AS count
              FROM `user`
             WHERE SHA1_PW <> 'invalidNonLocalUserPwHash'
               AND authentication_key <> %s """, (id,))
            count = int(cursor.fetchone()[0])

        return count == 0

MigrateMgr.instance().add(NonLocalUsersPasswordHashInvalidating())


