# -*- coding: utf-8 -*-
from trac.core import Component, implements
from trac.util.translation import _
from trac.admin.api import IAdminPanelProvider

from multiproject.common.projects import Projects
from multiproject.common.projects.project import HomeProject
from multiproject.common.notifications.email import EmailNotifier
from multiproject.core.configuration import conf


class ProjectStorageUsageAdmin(Component):
    implements(IAdminPanelProvider)

    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield ('projects', _('Projects'), 'storageusage', _('Storage usage'))

    def render_admin_panel(self, req, cat, page, path_info):
        req.perm.require("TRAC_ADMIN")

        api = Projects()
        sizes = api.get_storage_sizes()
        baseurl = conf.url_projects_path + "/"
        sysinfo = api.get_storage_info()
        modified = api.get_storage_csv_modification_time()

        return 'admin_storage_usage.html' , {'storages'   : sizes,
                                             'project_url': baseurl,
                                             'sysinfo'    : sysinfo,
                                             'modified'   : modified
                                            }


class StorageUsageNotifier(object):
    def tabspace(self, len):
        if len <= 15:
            return (15 - len) * ' '
        else:
            return ""

    def notify_now(self, env):
        api = Projects()
        home_project = HomeProject()
        listofprojects = ""
        projects = api.get_notified_projects()
        for name in projects.keys():
            if projects[name].notifynow:
                listofprojects += name + self.tabspace(len(name)) + str(projects[name].totalsize) + "\n"
        if len(listofprojects) > 0:
            # TODO: Move into template
            message = "These projects exceeded system storage limit:\n(storage limit = " +\
                      str(long(conf.storage_locking_limit)) + " bytes)\n\n"
            message += listofprojects
            mail = EmailNotifier(env, "Project(s) exceeded storage limits", message)
            mail.notify_system_admins(home_project)
