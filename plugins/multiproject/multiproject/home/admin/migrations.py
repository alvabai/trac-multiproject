# -*- coding: utf-8 -*-
from trac.core import Component, implements
from trac.admin.api import IAdminPanelProvider

from multiproject.core.migration import MigrateMgr
from multiproject.core.configuration import Configuration
conf = Configuration.instance()

# FIXME: This import is needed to notice all migrations (the module __init__
# has specific code for it)...
from multiproject.core.migrations import *


class MigrationAdminPanel(Component):
    """
    Module provides a listing of applied and available database migrations.

    .. NOTE:: Migration panel **is not** capable to run migrations.

    """
    implements(IAdminPanelProvider)

    # Part of IAdminPanelProvider interface
    def get_admin_panels(self, req):
        """ Introduce new item into admin navigation panel
        """
        if conf.resolveProjectName(self.env) == "home":
            if 'TRAC_ADMIN' in req.perm:
                yield ('general', 'General', 'migrations', 'Migrations')

    def set_upgrade(self, migrate, version):
        update_pkg = version.split(' ')[0]
        migrate.install(update_pkg)

    def __get_migrations(self):
        instance = MigrateMgr.instance()

        installed = instance.last_installed_migration_id()

        status = 'installed'
        items = instance.sort_clients()
        items.sort()

        migrations = []
        for (id, migration) in items:
            migrations.append((migration, status))
            if installed == id:
                status = 'new'
        return migrations

    # Part of IAdminPanelProvider interface
    def render_admin_panel(self, req, cat, page, path_info):
        """ Renders updates admin panel page
        """
        req.perm.require('TRAC_ADMIN')

        data = {}
        data['migrations'] = self.__get_migrations()

        return 'admin_migrations.html', data
