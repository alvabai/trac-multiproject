# -*- coding: utf-8 -*-
import csv
import time

from trac.core import Component, implements
from trac.util.translation import _
from trac.admin.api import IAdminPanelProvider, os

from multiproject.common.projects import commands
from multiproject.common.projects import HomeProject
from multiproject.common.projects.project import ProjectSizeTemplate, ProjectNotifications
from multiproject.common.notifications.email import EmailNotifier
from multiproject.core.configuration import Configuration
conf = Configuration.instance()


class ProjectStorageUsageAdmin(Component):
    implements(IAdminPanelProvider)

    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield ('projects', _('Projects'), 'storageusage', _('Storage usage'))

    def render_admin_panel(self, req, cat, page, path_info):
        req.perm.require("TRAC_ADMIN")

        sizes = self.get_storage_sizes()
        baseurl = conf.url_projects_path + "/"
        sysinfo = self.get_storage_info()
        modified = self.get_storage_csv_modification_time()

        return 'admin_storage_usage.html', {'storages': sizes,
                                            'project_url': baseurl,
                                            'sysinfo': sysinfo,
                                            'modified': modified}

    def get_storage_sizes(self):

        projectsinfo = []
        errorlimit = long(conf.storage_locking_limit)
        warninglimit = long(conf.storage_warning_limit)
        try:
            reader = csv.reader(open(conf.generated_content_dir + "/" + conf.storage_usage, "rb"))
            for row in reader:
                if len(row) >= 4:
                    total = long(row[1]) + long(row[2]) + long(row[3])
                    state = ""
                    if total > errorlimit > 0:
                        state = " limit"
                    elif total > warninglimit > 0:
                        state = " warn"
                    projectsinfo.append(ProjectSizeTemplate(
                        total, row[0], row[1], row[2], row[3], state))
        except Exception, e:
            conf.log.exception("Cannot load storage usage statistics.")

        return sorted(projectsinfo, key=lambda project: project.total_space, reverse=True)[:int(conf.max_items_shown)]

    def get_storage_info(self):
        rootpath = conf.sys_root
        api = commands.ProjectsInfo()
        info = api.disk_free(rootpath)
        info[0] = rootpath
        return info

    def get_storage_csv_modification_time(self):
        api = commands.ProjectsInfo()
        filename = os.path.join(conf.generated_content_dir, conf.storage_usage)
        if not os.path.exists(filename):
            return None
        return time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime(api.file_modified(filename)))


class StorageUsageNotifier(object):
    def tabspace(self, len):
        if len <= 15:
            return (15 - len) * ' '
        else:
            return ""

    def notify_now(self, env):
        home_project = HomeProject()
        listofprojects = ""
        projects = self.get_notified_projects()
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

    def get_notified_projects(self):

        def is_week_gone(today, lastsend):
            if (today - long(lastsend)) < 604800: # week in seconds
                return False
            else:
                return True

        projects = {}
        errorlimit = long(conf.storage_locking_limit)
        today = long(time.time())
        notifications_csv = os.path.join(conf.generated_content_dir, conf.notifications_file)
        usage_csv = os.path.join(conf.generated_content_dir, conf.storage_usage)
        try:
            readnew = csv.reader(open(usage_csv, "rb"))
            for row in readnew:
                if len(row) >= 4:
                    total = long(row[1]) + long(row[2]) + long(row[3])
                    if total > errorlimit > 0:
                        projects[row[0]] = ProjectNotifications(today, total, True)
        except Exception, e:
            conf.log.exception("Failed the read projects storage information")

        try:
            readold = csv.reader(open(notifications_csv, "rb"))
            for row in readold:
                if len(row) >= 2:
                    if projects[row[0]]:
                        projects[row[0]].notifynow = is_week_gone(today, row[1])
                        if projects[row[0]].notifynow:
                            projects[row[0]].notifytime = today
                        else:
                            projects[row[0]].notifytime = row[1]
        except Exception, e:
            conf.log.exception("Failed the read notification times from file")

        try:
            writer = csv.writer(open(notifications_csv, 'w'),
                delimiter='\n', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([s.encode("utf-8") + "," + str(projects[s].notifytime) for s in projects.keys()])
        except Exception, e:
            conf.log.exception("Failed the write notification times to file")

        return projects
