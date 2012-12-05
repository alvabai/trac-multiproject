# -*- coding: utf-8 -*-
"""
Adds local user organization for local users not already having one.
"""
from multiproject.core.db import admin_query
from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.permissions import CQDEOrganizationStore
from multiproject.core.users import User


# It seemed that "from multiproject.core.auth.local_auth import LocalAuthentication" failed,
# so hard-coding it here:
LOCAL = 'LocalDB'


class MissingOrganizations(MigrateBase):

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = __doc__
        self._was_downgraded = False

    def upgrade(self):
        if self.applied():
            print "Migration already applied".rjust(12)
            return True

        org_store = CQDEOrganizationStore.instance()
        user = User()
        organization_ids = org_store.get_organization_keys(user, LOCAL)

        if not organization_ids or len(organization_ids) > 1:
            print "Local organization was not found!"
            return False

        local_organization_id = organization_ids[0]

        queries = ["""
                INSERT INTO user_organization (user_key, organization_key)
                SELECT user_id, {organization_id}
                FROM user WHERE user_id NOT IN (SELECT user_key FROM user_organization)
                AND authentication_key IN (SELECT id FROM authentication
                                           WHERE method = '{method}')
           """.format(organization_id=local_organization_id, method=LOCAL)]
        return self.manager.db_upgrade(queries)

    def downgrade(self):
        if not self.applied():
            print "Migration was not applied."
            return True
        else:
            print "Migration cannot be downgraded."
            self._was_downgraded = True
            return True

    def applied(self):
        """
        Check if column exists or not
        :returns: True if exists, otherwise False
        """
        if self._was_downgraded:
            return False
        with admin_query() as cursor:
            cursor.execute('''
                SELECT count(*) FROM user
                WHERE user_id NOT IN (SELECT user_key FROM user_organization)
                AND authentication_key IN (SELECT id FROM authentication WHERE method = '{0}')
            '''.format(LOCAL))
            row = cursor.fetchone()
            return row[0] == 0

MigrateMgr.instance().add(MissingOrganizations())
