# -*- coding: utf-8 -*-
"""
Migration to remove meta permissions
"""
from trac.perm import PermissionSystem

from multiproject.core.db import admin_query, cursors
from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.permissions import get_permission_id
from multiproject.core.util.mockenv import MockEnvironment


class RemoveMetaPerms(MigrateBase):

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = self.__doc__
        self.pretend_to_be_not_applied = False

    def upgrade(self):
        if self.applied():
            return


        meta_perms = ['VIEW', 'MODIFY', 'CREATE', 'DELETE']
        meta_perm_ids = []
        perm_map = {}

        for meta_perm in meta_perms:
            meta_perm_ids.append(get_permission_id(meta_perm))

        # retrieve all permissions and build map of {'metaperm': [normal perm ids]}
        # get straight from the db since eg. home env does not have all permissions in it

        for perm in PermissionSystem(MockEnvironment()).get_actions():
            for meta_perm in meta_perms:
                if perm.endswith(meta_perm):
                    perm_map.setdefault(meta_perm, []).append(get_permission_id(perm))

        # combine so that DELETE permission for instance contains VIEW as well

        gives = {}
        gives['DELETE'] = ['DELETE', 'VIEW', 'MODIFY', 'CREATE']
        gives['CREATE'] = ['CREATE', 'VIEW', 'MODIFY']
        gives['MODIFY'] = ['MODIFY', 'VIEW']
        gives['VIEW'] = ['VIEW']

        combined_map = {}
        for what, metaperms in gives.iteritems():
            perms = []
            for p in metaperms:
                perms.extend(perm_map[p])
            combined_map[what] = perms

        perm_map = combined_map

        queries = []
        # previous get_permission_id calls may create new permissions, that are not in this transaction
        # hack around that ... verified manually and via CHECK TABLE that the result is consistent
        queries.append('SET foreign_key_checks = 0')

        # replace meta perms
        for meta_perm in meta_perms:
            meta_perm_id = get_permission_id(meta_perm)
            # go trough all groups having this permission
            with admin_query(cursors.DictCursor) as cursor:
                cursor.execute('SELECT group_key FROM group_permission WHERE permission_key=%s',
                    meta_perm_id)
                for row in cursor:
                    group_key = row['group_key']
                    for new_perm in perm_map[meta_perm]:
                        query = 'REPLACE INTO `group_permission` SET `group_key`=%s, `permission_key`=%s' % \
                            (group_key, new_perm)
                        queries.append(query)

        # delete metaperms
        for meta_perm in meta_perms:
            queries.append("DELETE FROM `action` WHERE `action_string` = '%s'" % meta_perm)
        for id in meta_perm_ids:
            queries.append("DELETE FROM group_permission WHERE permission_key = %s" % id)

        queries.append('SET foreign_key_checks = 1')
        return self.manager.db_upgrade(queries)

    def downgrade(self):
        # cannot be downgraded, but should work without them
        pass

    def applied(self):
        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM action WHERE action_string='VIEW'")
            return cursor.fetchone() is None


MigrateMgr.instance().add(RemoveMetaPerms())
