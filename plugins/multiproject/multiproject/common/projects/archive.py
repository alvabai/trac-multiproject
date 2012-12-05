import MySQLdb, shutil, os
from datetime import date

from trac.notification import NotificationSystem

from multiproject.common.projects import Project
from multiproject.common.projects.commands import Command
from multiproject.common.projects.commands import Commander
from multiproject.common.projects.commands import CreateTracDatabase
from multiproject.common.projects.commands import ListUpProject
from multiproject.common.projects.commands import SetPermissions
from multiproject.core.db import admin_query, safe_string, safe_int
from multiproject.core.configuration import conf
from multiproject.core.files.files_conf import FilesConfiguration
from multiproject.core.permissions import CQDEUserGroupStore, get_special_users
from multiproject.core.users import get_userstore


class ProjectArchive(object):

    def __init__(self):
        self.archive_path = conf.archive_path

    def list(self):
        """ List projects in archive
        """
        query = """
        SELECT * FROM project_archive
        WHERE removed_at IS NULL
        """
        return self.query_archived_projects(query)

    def archive(self, project):
        """ Archive a given project
        """
        process = self.__create_archiving_process(project)

        commander = Commander()
        for step in process:
            if not commander.run(step):
                conf.log.debug("Archiving failed on step: " + step.name)
                conf.log.debug("    project: " + str(project.env_name))
                conf.log.debug("    message: " + str(step.errormsg))
                # We wont rollback archiving even when error occurs
                return False
        return True

    def restore(self, project_archive_id, notifier):
        """ Restore archived project
        """
        project = self.get_archived_project(project_archive_id)
        project.id = None

        process = self.__create_restoring_process(project, notifier)
        commander = Commander()

        for step in process:
            if not commander.run(step):
                conf.log.debug("Restoring failed on step: " + step.name)
                conf.log.debug("    project: " + str(project.env_name))
                conf.log.debug("    message: " + str(step.errormsg))
                # No rollbacks
                return False
        return True

    def remove_expired(self):
        """ Remove all projects that have been in archive long enough
        """
        query = """
        SELECT * FROM project_archive
        WHERE remove_due < now() AND removed_at IS NULL
        """
        projects = self.query_archived_projects(query)

        project_count = len(projects)
        remove_count = 0
        fail_count = 0
        status = False

        for project in projects:
            status = self.remove(project.project_archive_id)
            if status:
                remove_count += 1
            else:
                fail_count += 1

        msg = str(remove_count) + " projects removed and "
        msg += str(fail_count) + " failed of "
        msg += str(project_count) + " expired projects."
        return msg

    def remove(self, project_archive_id):
        """ Remove project from archive
        """
        archived_project = self.get_archived_project(project_archive_id)
        if not self.remove_project_archive_folder(archived_project):
            conf.log.warning("Could not remove archive folder")
            return False
        if not self.mark_removed(archived_project):
            conf.log.warning("Could not mark removed")
            return False
        return True


    def remove_project_archive_folder(self, project):
        """ Remove archived project folder
        """
        try:
            shutil.rmtree(project.archive_path)
        except Exception, e:
            conf.log.exception(e)
            return False
        return True

    def mark_removed(self, project):
        """ Mark archived project removed
        """
        # No rollback, use the "read" connection
        with admin_query() as cursor:
            try:
                cursor.callproc("mark_archived_project_removed", [project.project_archive_id])
            except:
                conf.log.exception("Error marking project removed!")
                return False
        return True

    # TODO: Too much similar to Project.get_projects_with_params? Combine whole class to Project?
    def get_projects_with_params(self, username, perm, namelike=None, categories=None):
        """
        :returns: a list of archived projects where user have right for permission (action).
        """
        categories = categories or []
        user = get_userstore().getUser(username)
        user_organization = user.organization_keys

        # Get subjects
        subjects = set([username])
        subjects.update(get_special_users(username))

        # Construct comma separated lists for queries
        actions_str = ','.join("'%s'" % safe_string(p) for p in [perm, 'TRAC_ADMIN'])
        subjects_str = ','.join("'%s'" % safe_string(subject) for subject in subjects)
        categories_str = ','.join("'%s'" % safe_string(cat) for cat in categories)

        query = """
        SELECT DISTINCT pa.* FROM project_archive AS pa
        INNER JOIN `group` ON group.trac_environment_key = (
            SELECT environment_id
            FROM trac_environment
            WHERE identifier = pa.environment_name
        )
        INNER JOIN group_permission ON group_permission.group_key = group.group_id
        INNER JOIN action ON group_permission.permission_key = action.action_id
        LEFT JOIN user_group ON user_group.group_key = group.group_id
        LEFT JOIN user ON user.user_id = user_group.user_key
        """

        # NOTE! When project is archived/removed, the category information is also removed
        if categories:
            query += ("INNER JOIN project_categories ON pa.orig_project_id = project_categories.project_key "
                      "INNER JOIN categories ON categories.category_id = project_categories.category_key ")

        query += ("LEFT JOIN organization_group ON organization_group.group_key = group.group_id "
                  "WHERE (user.username IN (%s) " % subjects_str)

        if not user_organization:
            query += "OR organization_group.organization_key = NULL )"
        else:
            # List user organizations as safe int, separated with comma: (1,5,3,65)
            orc = lambda org_key: str(safe_int(org_key))
            query += "OR organization_group.organization_key IN (%s) ) " % ','.join(map(orc, user_organization))

        query += "AND action.action_string IN(" + actions_str + ") "

        if categories:
            query += "AND categories.category_name IN(" + categories_str + ") "

        if namelike:
            conditions = []
            search_strs = namelike.split(' ')
            for search in search_strs:
                if not search == '':
                    search = safe_string(search)
                    conditions.append("pa.project_name LIKE '%" + search + "%'")

            where = " OR ".join(conditions)
            query += "AND (" + where + ") "
        query += "ORDER BY pa.project_name"

        return self.query_archived_projects(query)


    def __create_archiving_process(self, project):
        """ Create process for archiving project
        """
        process = [CreateProjectArchiveDbRecord(project), CreateArchiveFolder(project), ArchiveProjectFolder(project),
                   ArchiveRepository(project), ArchiveWebDav(project), ArchiveProjectTeam(project),
                   ArchiveProjectDb(project)]
        return process

    def __create_restoring_process(self, project, env):
        """ Create restoring process for restoring archived project
        """
        process = [CreateTracDatabase(project), RestoreEnvironment(project), RestoreDav(project),
                   RestoreRepository(project), RestoreDatabase(project), RemoveProjectArchiveDbRecord(project),
                   ListUpProject(project), SetPermissions(project), NotifyAuthorAboutRestore(project, env),
                   CleanUpArchiveFolder(project)]
        return process

    def get_archived_project(self, project_archive_id):
        """
        Get project from archive

        :param int project_archive_id: Id of the project archive
        :returns: The archived project if found (one), otherwise None
        """
        query = """
        SELECT * FROM project_archive
        WHERE project_archive_id = {0}
        LIMIT 1
        """.format(safe_string(str(project_archive_id)))

        projects = self.query_archived_projects(query)
        if len(projects) == 1:
            return projects[0]

        return None

    def query_archived_projects(self, query):
        """ Returns a list of archived projects given with query
        """
        projects = []
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for project in cursor.fetchall():
                    # Create regular project
                    prj = Project(id = project[1],
                                  env_name = project[3],
                                  project_name = project[2],
                                  description = None,
                                  author_id = project[4],
                                  created = project[5],
                                  parent_id = project[6])

                    # Add some archiving parameters
                    prj.archive_folder_name = project[7]
                    prj.archive_path = conf.archive_path + "/" + project[7]
                    prj.archive_date = project[8]
                    prj.remove_due = project[9]
                    prj.removed_at = project[10]
                    prj.project_archive_id = project[0]

                    projects.append(prj)

            except:
                conf.log.exception("Querying archived projects failed with query '''%s'''" % query)

        return projects


class CloneFolder(Command):
    """ This can be inherited to make easily commands for cloning folders.
        Not to be used directly.
    """

    def __init__(self):
        Command.__init__(self)
        self.source = None
        self.destination = None

    def do(self):
        try:
            if not os.path.exists(self.source):
                conf.log.debug("Folder doesn't exist! (" + self.source + ")")
                return False
            if os.path.exists(self.destination):
                conf.log.debug("Path already exists! (" + self.destination + ")")
                conf.log.debug("Trying to archive project that is already archived?")
                return False
            shutil.copytree(self.source, self.destination)
        except Exception, e:
            conf.log.debug("Unexpected error in copying folder (" + self.source + ") into (" + self.destination + ")")
            conf.log.exception(e)
            return False
        return True

    def undo(self):
        try:
            if os.path.exists(self.destination):
                shutil.rmtree(self.destination)
        except Exception, e:
            conf.log.exception(e)
            return False
        return True


class CreateProjectArchiveDbRecord(Command):
    """ Clones project record from projects table into archive
    """
    def __init__(self, project):
        Command.__init__(self)
        self.name = "CreateProjectArchiveDbRecord"
        self.project = project
        self.archive_id = None

    def do(self):
        self.errormsg = "Archiving error!"

        with admin_query() as cursor:
            try:
                cursor.callproc("archive_project_record", [self.project.id])
                row = cursor.fetchone()
                if not row:
                    conf.log.debug("Archiving failed: No row")
                    return False
                self.project.archive_id = row[0]
                if not self.project.archive_id:
                    conf.log.debug("Archiving failed: No id")
                    return False
            except Exception, e:
                self.errormsg = "Could not archive project record in db"
                conf.log.exception(e)
                return False

        self.errormsg = ""
        return True

    def undo(self):
        with admin_query() as cursor:
            try:
                cursor.callproc("remove_archived_project_record", [self.project.archive_id])
            except Exception, e:
                conf.log.exception(e)
                return False
        return True


class CreateArchiveFolder(Command):

    def __init__(self, project):
        Command.__init__(self)
        self.name = "CreateArchiveFolder"
        self.project = project

    def do(self):
        self.date = date.today()
        # Create folder path in format "20101224_someproject_447"
        self.base_path = conf.archive_path + "/"
        self.folder_name = str(self.date.strftime('%Y%m%d_')) + self.project.env_name + "_" + str(self.project.archive_id)
        self.project.archive_folder_name = self.folder_name
        self.project.archive_path = self.base_path + self.folder_name

        if os.path.exists(self.project.archive_path):
            conf.log.debug("Failed to create path for project archive. Path exists.")
            return False
        os.makedirs(self.project.archive_path)

        # Update project archive folder
        with admin_query() as cursor:
            try:
                cursor.callproc("update_project_archive_folder", [self.project.archive_id,
                                                                  self.project.archive_folder_name])
            except:
                return False
        return True

    def undo(self):
        try:
            if os.path.exists(self.path):
                shutil.rmtree(self.path)
        except:
            return False
        return True


class ArchiveProjectFolder(CloneFolder):

    def __init__(self, project):
        CloneFolder.__init__(self)
        self.name = "ArchiveProjectFolder"
        self.project = project
        self.source = self.project.trac_fs_path

    def do(self):
        self.destination = self.project.archive_path + "/trac"
        return CloneFolder.do(self)


class ArchiveRepository(CloneFolder):

    def __init__(self, project):
        CloneFolder.__init__(self)
        self.name = "ArchiveRepository"
        self.project = project
        self.source = self.project.vcs_fs_path

    def do(self):
        self.destination = self.project.archive_path + "/vcs"
        return CloneFolder.do(self)


class ArchiveWebDav(CloneFolder):

    def __init__(self, project):
        CloneFolder.__init__(self)
        self.name = "ArchiveWebDav"
        self.project = project
        self.source = self.project.dav_fs_path

    def do(self):
        self.destination = self.project.archive_path + "/dav"
        if not os.path.exists(self.source):
            return True

        return CloneFolder.do(self)


class ArchiveProjectDb(Command):

    def __init__(self, project):
        Command.__init__(self)
        self.name = "ArchiveProjectDb"
        self.project = project

    def do(self):
        self.dump_file = self.project.archive_path + "/database.sql"
        self.cmd = "mysqldump -u " + conf.db_user + " "
        self.cmd += "--password=" + conf.db_password + " "
        self.cmd += "--host=" + conf.db_host + " "
        self.cmd += self.project.env_name
        self.cmd += " > " + self.dump_file

        if os.system(self.cmd) != 0:
            conf.log.debug("Failed on creating mysqldumb with command:")
            conf.log.debug("     " + self.cmd)
            return False
        return True

    def undo(self):
        if os.path.exists(self.dump_file):
            if os.remove(self.dump_file):
                return True
        return False


class ArchiveProjectTeam(Command):
    """ Store users and permissions into flat file

        This file will be sent for author if project is restored
    """
    def __init__(self, project):
        Command.__init__(self)
        self.name = "ArchiveProjectTeam"
        self.project = project
        self.groups = CQDEUserGroupStore(project.trac_environment_key)

    def do(self):
        self.team = self.project.archive_path + "/team.txt"
        f = open(self.team, 'w')

        f.write("#### Users in groups ####\n")
        for user, group in self.groups.get_all_user_groups():
            f.write(user + ' : ' + group + "\n")

        f.write("\n#### Group permissions ####\n")
        for group, perm in self.groups.get_all_group_permissions():
            f.write(group + ' : ' + perm + "\n")

        f.write("\n#### Group organizations ####\n")
        for org, group in self.groups.get_all_organization_groups():
            f.write(org + ' : ' + group + "\n")

        f.close()
        return True

    def undo(self):
        if os.path.exists(self.team):
            if os.remove(self.team):
                return True
        return False

class RestoreEnvironment(CloneFolder):

    def __init__(self, project):
        CloneFolder.__init__(self)
        self.name = "RestoreEnvironment"
        self.project = project
        self.source = self.project.archive_path + "/trac"
        self.destination = os.path.join(conf.sys_projects_root, self.project.env_name)

        if not self.project.env_name:
            raise Exception("Incorrect data")

class RestoreDav(CloneFolder):

    def __init__(self, project):
        CloneFolder.__init__(self)
        self.name = "RestoreDav"
        self.project = project
        self.source = self.project.archive_path + "/dav"
        self.destination = os.path.join(FilesConfiguration().sys_dav_root, self.project.env_name)

    def do(self):
        if not os.path.exists(self.source):
            return True

        return CloneFolder.do(self)

class RestoreRepository(CloneFolder):

    def __init__(self, project):
        CloneFolder.__init__(self)
        self.name = "RestoreRepository"
        self.project = project
        self.source = self.project.archive_path + "/vcs"
        self.destination = conf.sys_vcs_root + "/" + self.project.env_name

class RestoreDatabase(Command):

    def __init__(self, project):
        Command.__init__(self)
        self.name = "RestoreProjectDatabase"
        self.project = project

    def do(self):
        self.dump_file = self.project.archive_path + "/database.sql"
        self.cmd = "mysql -u " + conf.db_user + " "
        self.cmd += "--password=" + conf.db_password + " "
        self.cmd += "--host=" + conf.db_host + " "
        self.cmd += self.project.env_name
        self.cmd += " < " + self.dump_file

        if os.system(self.cmd) != 0:
            conf.log.debug("Failed on restoring mysql dump:")
            conf.log.debug("     " + self.cmd)
            return False
        return True

    def undo(self):
        return True


class RemoveProjectArchiveDbRecord(Command):
    """ Clones project record from projects table into archive
    """
    def __init__(self, project):
        Command.__init__(self)
        self.name = "RemoveProjectArchiveDbRecord"
        self.project = project

    def do(self):
        with admin_query() as cursor:
            try:
                cursor.callproc("remove_archived_project_record", [self.project.project_archive_id])
            except Exception, e:
                conf.log.exception(e)
                return False
        return True

    def undo(self):
        with admin_query() as cursor:
            try:
                cursor.callproc("archive_project_record", [self.project.id])
                row = cursor.fetchone()
                if not row:
                    conf.log.debug("Archiving failed: No row")
                    return False
                self.project.archive_id = row[0]
                if not self.project.archive_id:
                    conf.log.debug("Archiving failed: No id")
                    return False
            except Exception, e:
                self.errormsg = "Could not archive project record in db"
                conf.log.exception(e)
                return False

        self.errormsg = ""
        return True


class NotifyAuthorAboutRestore(Command):

    def __init__(self, project, env):
        Command.__init__(self)
        self.name = "NotifyAuthorAboutRestore"
        self.project = project
        self.notifier = NotificationSystem(env)
        from_email = env.config['notification'].get('smtp_from')
        replyto_email = env.config['notification'].get('smtp_replyto')
        self.from_email = from_email or replyto_email

    def do(self):
        author = self.project.author
        try:
            if author:
                txt = "Your project '" + self.project.project_name + "' have been restored and should "
                txt += "be accessible in " + self.project.get_url() + "\n\n"
                txt += "Permissions have not been restored automatically. You should add manually all "
                txt += "permissions again. Listings in the below will help if you want to give similar "
                txt += "permissions that project used to have.\n\n"
                team = self.project.archive_path + "/team.txt"
                f = open(team, 'r')
                txt += f.read()
                f.close()
                self.notifier.send_email(self.from_email, author.mail, txt)
        except Exception, e:
            conf.log.debug("Writing restore notification failed.")
            conf.log.exception(e)
        return True

    def undo(self):
        # You can't undo mail sending
        return False


class CleanUpArchiveFolder(Command):

    def __init__(self, project):
        Command.__init__(self)
        self.name = "CleanUpArchiveFolder"
        self.project = project

    def do(self):
        try:
            shutil.rmtree(self.project.archive_path)
        except Exception, e:
            conf.log.exception(e)
            return False
        return True

    def undo(self):
        # You can't restore removed folder
        return False
