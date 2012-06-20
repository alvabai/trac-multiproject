# -*- coding: utf-8 -*-
from trac.admin.api import IAdminPanelProvider
from trac.core import Component, implements, TracError
from trac.util.translation import _
from trac.web.chrome import add_notice, add_warning

from multiproject.core.permissions import CQDESuperUserStore


class SuperUsersPanel(Component):
    implements(IAdminPanelProvider)

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        store = CQDESuperUserStore.instance()
        if store.is_superuser(req.authname):
            yield ('permissions', _('Permissions'), 'superusers', _('Super users'))

    def render_admin_panel(self, req, cat, page, path_info):
        self.store = CQDESuperUserStore.instance()
        if not self.store.is_superuser(req.authname):
            raise TracError("You should not see this view.", "Permission denied!")
        
        if req.method == 'POST':
            if req.args.get('add'):
                self.add_superuser(req)
            elif req.args.get('remove'):
                self.remove_superuser(req)
        
        return 'admin_superusers.html', {'super_users':self.store.get_superusers()}

    def add_superuser(self, req):
        username = req.args.get('username')
        if username:
            if self.store.add_superuser(username):
                add_notice(req, "User " + username + " is superuser.")
            else:
                add_warning(req, "Adding superuser failed!")
        else:
            add_warning(req, "Username not given")
    
    def remove_superuser(self, req):
        username = req.args.get('username')
        if username:
            if self.store.remove_superuser(username):
                add_notice(req, "User " + username + " removed from superusers.")
            else:
                add_warning(req, "Removing superuser failed!")
        else:
            add_warning(req, "Username not given")
