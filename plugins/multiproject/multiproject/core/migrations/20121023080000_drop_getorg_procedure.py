# -*- coding: utf-8 -*-
"""
Removes get_organization_id procedure
"""
from multiproject.core.db import admin_query
from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.configuration import conf


class DropGetOrgProcedure(MigrateBase):

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = self.__doc__
        self.pretend_to_be_not_applied = False

    def upgrade(self):
        """
        Runs the upgrade queries
        """
        if self.applied():
            return

        queries = ['DROP PROCEDURE IF EXISTS `get_organization_id`']
        return self.manager.db_upgrade(queries)

    def downgrade(self):
        """
        Runs the downgrade queries
        """
        queries = ['''
        CREATE PROCEDURE `get_organization_id`(organization_name VARCHAR(128))
        BEGIN
            SELECT organization_id FROM organization
            WHERE organization.organization_name = organization_name;
        END
        ''']

        return self.manager.db_upgrade(queries)

    def applied(self):
        """
        Check if migration is already applied
        :return: True if already applied, otherwise False
        """
        with admin_query() as cursor:
            cursor.execute('''
                SHOW PROCEDURE STATUS
                WHERE
                    Name = 'get_organization_id' AND
                    Db = '{0}'
            '''.format(conf.db_admin_schema_name))
            return cursor.rowcount == 0


MigrateMgr.instance().add(DropGetOrgProcedure())
