# -*- coding: utf-8 -*-
"""
Contents of this module
"""
import csv
import math
import time

from trac.util.translation import _
from trac.core import TracError

from multiproject.common.projects.commands import Commander, CreateTracDatabase, CloneVersionControl, CreateTracVersionControl, \
    InitCommitHooks, CreateTracEnvironment, ConfigureTrac, ListUpProject, SetPermissions, MakeProjectPublic, CreateDav, \
    CreateDownloads, InitTracWiki, TruncateDefaultInformation, RefreshStatistics, ConfigureFilesystemPermissions, ProjectsInfo
from multiproject.common.projects.project import Project, ProjectSizeTemplate, ProjectNotifications
from multiproject.core.cache import ProjectCache
from multiproject.core.categories import CQDECategoryStore
from multiproject.core.configuration import conf
from multiproject.core.db import admin_query, admin_transaction, safe_string, safe_int, cursors
from multiproject.core.exceptions import ProjectValidationException
from multiproject.core.permissions import CQDEPermissionPolicy, CQDEAuthenticationStore, CQDEPermissionHelper


class Projects(object):
    """ Api class for multiproject plugin. Used for actions like creating,
        removing and listing projects
    """

    def create_project(self, project, services):
        """ Creates project a new project

            Attributes:
            long_name   = Short description of a project
            short_name  = Actually a project identifier string (max 32 chars)
            owner       = Username of creator of the project
            services[*]     = Services
        """
        # Check if project exists
        if self.project_environment_exists(project.env_name):
            raise ProjectValidationException("This project already exists! Change identifier.")

        # Check version control type
        if services['vcs_type'] not in conf.supported_scm_systems:
            raise ProjectValidationException("Unsupported source control management system.")

        # Try validate project
        project.validate()

        # Build list of needed commands
        commander = Commander()
        commandlist = []
        commandlist.append(CreateTracDatabase(project))

        # Create a new repository or clone an existing one
        if project.parent_project:
            commandlist.append(CloneVersionControl(project))
        else:
            commandlist.append(CreateTracVersionControl(project, services))

        commandlist.append(InitCommitHooks(project, services))
        commandlist.append(CreateTracEnvironment(project, services))
        commandlist.append(ConfigureTrac(project, services))
        commandlist.append(ListUpProject(project))
        commandlist.append(SetPermissions(project))

        if project.published:
            commandlist.append(MakeProjectPublic(project))

        commandlist.append(CreateDav(project))
        commandlist.append(CreateDownloads(project))
        commandlist.append(InitTracWiki(project))
        commandlist.append(TruncateDefaultInformation(project))
        commandlist.append(RefreshStatistics(project))
        commandlist.append(ConfigureFilesystemPermissions(project))

        # Run all commands, on failure roll all back
        for cmd in commandlist:
            if not commander.run(cmd):
                commander.rollallback()
                raise Exception

    def project_count(self):
        """ Number of projects
        """
        count = 0
        with admin_query() as cursor:
            cursor.execute("SELECT count(project_id) FROM projects")
            row = cursor.fetchone()
            # Since the query is a count, it will always return a value, or the execute
            # will throw an exception
            count = row[0]

        return count

    def public_project_count(self):
        """ Number of public projects
        """
        users = conf.getUserStore()

        # Chances are that we get these from the cache
        anon = users.getUser('anonymous')
        auth = None #users.getUser('authenticated')

        users_in = []
        if anon:
            users_in.append(str(safe_int(anon.id)))
        if auth:
            users_in.append(str(safe_int(auth.id)))
        users_in_str = ','.join(users_in)

        query = ("SELECT count(DISTINCT project_id) FROM projects "
                 "INNER JOIN `group` ON `group`.trac_environment_key = projects.trac_environment_key "
                 "INNER JOIN user_group ON user_group.group_key = `group`.group_id "
                 "WHERE user_group.user_key IN(%s)" % users_in_str)

        count = 0
        with admin_query() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()
            count = row[0]

        return count

    def project_environment_exists(self, env_name):
        """ Checks if a project with given identifier (env_name) exists
        """
        row = []
        query = """
        SELECT COUNT(project_id)
        FROM projects
        WHERE environment_name = %s
        """

        with admin_query() as cursor:
            try:
                cursor.execute(query, env_name)
                row = cursor.fetchone()
            except Exception, e:
                conf.log.exception(e)
                return False

        # Query always returns (or throws an exception) a value so just convert it to bool
        return bool(row[0])

    def is_project_owner(self, short_name, username):
        """ Check that username matches project's author
        """
        row = []
        store = conf.getUserStore()
        user = store.getUser(username)

        query = """
        SELECT author
        FROM projects
        WHERE environment_name = %s
        """

        with admin_query() as cursor:
            try:
                cursor.execute(query, short_name)
                row = cursor.fetchone()
            except Exception, e:
                conf.log.exception(e)
                return False

        if not row:
            return False
        if row[0] != user.id:
            return False
        return True

    def remove_project(self, project):
        """
        Removes existing project.

        :arg project: :class:`Project` to be removed.
        """
        vcs_type = conf.getVersionControlType(project.env_name)

        # Remove project from db
        cmd = ListUpProject(project)
        cmd.success = True
        cmd.undo()

        # Remove configuration
        cmd = ConfigureTrac(project, {'vcs_type': vcs_type})
        cmd.success = True
        cmd.undo()

        # Remove trac environment
        cmd = CreateTracEnvironment(project, {'vcs_type': vcs_type})
        cmd.success = True
        cmd.undo()

        cmd = CreateTracVersionControl(project, {'vcs_type': vcs_type})
        cmd.success = True
        cmd.undo()

        # Remove database
        cmd = CreateTracDatabase(project)
        cmd.success = True
        cmd.undo()

        cmd = CreateDav(project)
        cmd.undo()

        cmd = CreateDownloads(project)
        cmd.undo()

        return True

    def get_project_team(self, project_key):
        """ Returns a list of those users that have rights to project
        """
        query = ("SELECT DISTINCT user.* FROM user "
                 "INNER JOIN user_group ON user.user_id = user_group.user_key "
                 "INNER JOIN `group` ON user_group.group_key = group.group_id "
                 "INNER JOIN projects ON projects.trac_environment_key = group.trac_environment_key "
                 "WHERE projects.project_id = %d" % safe_int(project_key))
        user_store = conf.getUserStore()
        return user_store.query_users(query)

    def searchUserProjects(self, search_str, username):
        """ List projects that have identifier like search string
        """
        if search_str == '' or search_str.strip() == '*':
            return self.get_projects_with_rights(username, "VERSION_CONTROL_VIEW")
        else:
            return self.get_projects_with_params(username, "VERSION_CONTROL_VIEW",
                search_str.strip('*'))

    def get_project(self, project_id=None, env_name=None):
        """ Returns a project with a given id
            Usage.
                  projects.get_project(453)
                  projects.get_project(project_id = 453)
                  projects.get_project(env_name = "some_environment")
        """
        if env_name:
            project_id = self.get_project_id(env_name)

        if not project_id:
            return None

        # Try cache
        cache = ProjectCache.instance()
        project = cache.getProject(project_id)
        if project:
            return project

        query = ("SELECT * FROM projects WHERE projects.project_id = %d LIMIT 1" %
                 safe_int(project_id))

        projects = self.queryProjectObjects(query)
        if len(projects) > 0:
            cache.setProject(projects[0])
            return projects[0]
        return None

    def get_project_id(self, env_name):
        # Try from cache
        cache = ProjectCache.instance()
        id = cache.getProjectId(env_name)
        if id:
            return id

        # Get from db
        query = ("SELECT project_id FROM projects WHERE environment_name = '%s'" %
                 safe_string(env_name))

        with admin_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
                if row:
                    cache.setProjectId(env_name, row[0])
                    return row[0]
            except Exception, e:
                conf.log.exception(e)

    def get_projects_with_rights(self, username, action):
        """
        :returns: a list of projects where user have right for "action".

        .. note::

           Permissions coming via LDAP groups are not included in the results

        """
        userstore = conf.getUserStore()
        user = userstore.getUser(username)

        # Get actions
        policy = CQDEPermissionPolicy()
        actions = policy.get_granting_permissions(action)

        # Get subjects
        subjects = set([username])
        subjects.update(policy.get_special_users(username))

        # Surround string elements with ' and join them with comma
        actions_str = ','.join(["'{0}'".format(safe_string(action)) for action in actions])
        subjects_str = ','.join(["'{0}'".format(safe_string(subject)) for subject in subjects])
        organizations_str = ','.join(["{0}".format(safe_int(org_key)) for org_key in user.organization_keys])

        query = ("SELECT DISTINCT projects.* FROM projects "
                 "INNER JOIN `group` ON group.trac_environment_key = projects.trac_environment_key "
                 "INNER JOIN group_permission ON group_permission.group_key = group.group_id "
                 "INNER JOIN action ON group_permission.permission_key = action.action_id "
                 "LEFT JOIN user_group ON user_group.group_key = group.group_id "
                 "LEFT JOIN user ON user.user_id = user_group.user_key "
                 "LEFT JOIN organization_group ON organization_group.group_key = group.group_id "
                 "WHERE (user.username IN(%s) "
                 "OR organization_group.organization_key IN(%s)) "
                 "AND action.action_string IN(%s) "
                 "ORDER BY projects.project_name" % (subjects_str, organizations_str, actions_str))

        return self.queryProjectObjects(query)

    def get_projects_with_params(self, username, perm, namelike=None, categories=None):
        """ Returns a list of projects where user have right for "action".
        """
        categories = categories or []
        userstore = conf.getUserStore()
        user = userstore.getUser(username)
        user_organization = user.organization_keys

        # Get actions
        policy = CQDEPermissionPolicy()
        actions = policy.get_granting_permissions(perm)

        # Get subjects
        subjects = set([username])
        subjects.update(policy.get_special_users(username))

        # Construct comma separated lists for queries
        actions_str = ','.join("'%s'" % safe_string(action) for action in actions)
        subjects_str = ','.join("'%s'" % safe_string(subject) for subject in subjects)
        categories_str = ','.join("'%s'" % safe_string(cat) for cat in categories)

        query = ("SELECT DISTINCT projects.* FROM projects "
                 "INNER JOIN `group` ON group.trac_environment_key = projects.trac_environment_key "
                 "INNER JOIN group_permission ON group_permission.group_key = group.group_id "
                 "INNER JOIN action ON group_permission.permission_key = action.action_id "
                 "LEFT JOIN user_group ON user_group.group_key = group.group_id "
                 "LEFT JOIN user ON user.user_id = user_group.user_key ")

        if categories:
            query += ("INNER JOIN project_categories ON projects.project_id = project_categories.project_key "
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
                    conditions.append("projects.project_name LIKE '%" + search + "%'")

            where = " OR ".join(conditions)
            query += "AND (" + where + ") "
        query += "ORDER BY projects.project_name"
        return self.queryProjectObjects(query)

    def get_forkable_projects(self, username):
        return self.get_projects_with_rights(username, "VERSION_CONTROL_VIEW")

    def get_featured_projects(self, limit=None, count=None):
        """ List all featured projects
        """
        query = ("SELECT projects.*, project_selected.value AS priority FROM project_selected "
                 "INNER JOIN projects ON  project_selected.project_id = projects.project_id "
                 "ORDER BY priority ")

        if limit:
            if count:
                query += "LIMIT %d,%d" % (safe_int(limit), safe_int(count))
            else:
                query += "LIMIT %d" % safe_int(limit)

        projects = self.__queryProjectsWithDescr(query)
        return projects

    def update_featured_projects(self, projects):
        """ update featured projects
        """
        with admin_transaction() as cursor:
            try:
                # First cleanup selected projects
                query = "DELETE FROM project_selected"
                cursor.execute(query)

                # Then update new projects
                if len(projects) > 0:
                    query = "INSERT INTO project_selected (project_id,value) VALUES "

                    line = "((SELECT projects.project_id FROM projects WHERE environment_name = '%s'), %d)"
                    lines = []

                    for project, value in projects:
                        lines.append(line % (safe_string(project), safe_int(value)))

                    query += ",".join(lines)

                    cursor.execute(query)
            except:
                conf.log.exception("Update featured project transaction failed %s" % query)
                raise

    def get_authored_projects(self, user):
        """
        Get projects that are created by given user

        :param User user: User who is author of the project
        :returns: List of project objects
        """
        query = """
        SELECT projects.*
        FROM projects
        INNER JOIN user ON projects.author = user.user_id
        WHERE user.username = '{0}'
        ORDER BY project_name
        """.format(safe_string(user.username))

        return self.queryProjectObjects(query)

    def get_participated_projects(self, user, by_organization=False, by_ldap=False,
                                  public_only=False):
        """
        Get those projects that user has participated. Optionally can list by organization,
        or by public status.

        :param User user: User object
        :param boolean by_organization: List projects by organization
        :param boolean public_only: Get public projects as well
        :returns: List of Project objects
        """

        # Anonymous does not have organization
        if not user.organization_keys:
            by_organization = False

        and_anon_condition= ''
        union_all_organization_condition = ''
        union_all_ldap_condition = ''
        permission_helper = CQDEPermissionHelper.instance()
        perm_ids = ', '.join([str(safe_int(permission_helper.get_permission_id(action)))
                           for action in ('VIEW', 'TEAM_VIEW')])
        if public_only:
            # fetch anonymous user id
            # FIXME: Would be nice if we didn't have to do this all the time
            store = conf.getUserStore()
            anon = store.getUser('anonymous')
            if not anon:
                conf.log.warning("Error in get_participated_projects: No anonymous user obtained!")
                raise TracError("Error while fetching user's projects.")
            and_anon_condition = """
                AND EXISTS
                (SELECT group.trac_environment_key
                FROM `group`
                INNER JOIN user_group ON user_group.group_key = group.group_id
                INNER JOIN group_permission ON group.group_id = group_permission.group_key
                WHERE user_group.user_key = {anon_id}
                  AND group.trac_environment_key = projects.trac_environment_key
                  AND group_permission.permission_key IN ({perm_ids})
                )
            """.format(anon_id = safe_int(anon.id), perm_ids = perm_ids)

        if by_organization:
            # See if the user has access into projects through organizations
            union_all_organization_condition += """
                UNION ALL

                SELECT group.trac_environment_key
                FROM `trac_admin`.`group`
                INNER JOIN organization_group ON organization_group.group_key = group.group_id
                WHERE organization_group.organization_key IN({organization_ids})
            """.format(organization_ids =
                ', '.join([str(safe_int(org_id)) for org_id in user.organization_keys]))

        if by_ldap and conf.ldap_groups_enabled:
            # See if any ldap groups are allowed in environment
            auth_store = CQDEAuthenticationStore.instance()
            is_ldap_account = auth_store.is_ldap(user.authentication_key)
            if is_ldap_account:
                # See if user belongs to any of the allowed ldap groups
                ldapuser_store = conf.getAuthenticationStore()
                user_ldapgroups = ldapuser_store.getGroups(user.username)

                if user_ldapgroups:
                    union_all_ldap_condition = """
                    UNION ALL

                    SELECT group.trac_environment_key
                    FROM `trac_admin`.`group`
                    INNER JOIN ldapgroup_group ON ldapgroup_group.group_key = group.group_id
                    INNER JOIN ldapgroup ON ldapgroup.ldapgroup_id = ldapgroup_group.ldapgroup_key
                    WHERE ldapgroup.ldapgroup_name IN ({ldapgroup_names})
                    """.format(ldapgroup_names =
                        ', '.join(["'{0}'".format(safe_string(group)) for group in user_ldapgroups]))

        query = """
            SELECT projects.* FROM projects
            WHERE projects.trac_environment_key IN (
                SELECT group.trac_environment_key
                FROM `trac_admin`.`group`
                INNER JOIN user_group ON user_group.group_key = group.group_id
                WHERE user_group.user_key = {user_id}
                {union_all_organization}
                {union_all_ldap}
            )
            {and_anon}
            ORDER BY projects.project_name ASC
        """.format(user_id = safe_int(user.id),
            union_all_organization = union_all_organization_condition,
            union_all_ldap = union_all_ldap_condition,
            and_anon = and_anon_condition)

        conf.log.debug("queried participated projects with %s" % query)
        projects = self.queryProjectObjects(query)
        return projects

    def get_default_projects(self):
        """ Return a list of default projects and their names

            Default projects are shown always in the My Projects page
        """
        if not conf.default_projects:
            return []

        identifiers = ','.join(["'%s'" % prj for prj in conf.default_projects])
        query = """SELECT * FROM projects WHERE environment_name IN (%s)""" % identifiers

        projects = {}
        with admin_query() as cursor:
            cursor.execute(query)
            for prj in cursor:
                project = Projects.sqlToProject(prj)
                projects[project.env_name] = project

        project_list = []
        for identifier in conf.default_projects:
            if identifier in projects:
                project_list.append(projects[identifier])

        return project_list, set(projects.keys())

    def get_participated_public_projects(self, username):
        """ Get public projects username has participated in
        """
        store = conf.getUserStore()
        user = store.getUser(username)
        if not user:
            return []

        anon = store.getUser('anonymous')

        order = " ORDER BY projects.project_name"

        # We need projects where _both_ anonymous and the specified user exist
        query = """
        SELECT projects.environment_name AS name, projects.description AS description, projects.created AS date,
          '%(user_name)s' AS author, projects.project_name, projects.icon_id
        FROM projects
        INNER JOIN `group` ON group.trac_environment_key = projects.trac_environment_key
        INNER JOIN user_group ON user_group.group_key = group.group_id
        INNER JOIN `user` ON user_group.user_key = user.user_id
        WHERE user_group.user_key = %(user_id)d AND EXISTS
        (SELECT * FROM projects P
        INNER JOIN `group` ON `group`.trac_environment_key = P.trac_environment_key
        INNER JOIN user_group ON user_group.group_key = group.group_id
        WHERE user_group.user_key = %(anon_id)d AND projects.project_id = P.project_id)
        """ % {"user_name": safe_string(user.getDisplayName().encode('utf-8')),
               "user_id": safe_int(user.id), "anon_id": safe_int(anon.id)}
        query += order
        return self.__queryProjectsWithDescr(query)

    def get_newest_participated_projects(self, username, projectcount):
        """ Get those projects that user with 'username' has participated
            ordered by newest first, limited by projectcount
        """
        store = conf.getUserStore()
        user = store.getUser(username)

        query = "SELECT projects.*, '" + safe_string(
            user.getDisplayName().encode('utf-8')) + "' FROM projects "
        query += "INNER JOIN `group` ON group.trac_environment_key = projects.trac_environment_key "
        query += "INNER JOIN user_group ON user_group.group_key = group.group_id "
        query += "INNER JOIN user ON user_group.user_key = user.user_id "
        query += "WHERE user_group.user_key = %d " % safe_int(user.id)
        query += "ORDER BY projects.created DESC LIMIT %d" % safe_int(projectcount)

        return self.__queryProjects(query)

    def get_project_counts_per_category(self, username):
        # Try from cache
        cache = ProjectCache.instance()
        items = cache.get_project_counts_per_category(username)
        if items:
            return items

        anon_et_al = "(%s)"
        if username != 'anonymous':
            anon_et_al = "('anonymous', %s)"
        # Query public project count / category
        query = """SELECT pc.category_key, COUNT(pc.project_key)
                    FROM project_categories AS pc
                    INNER JOIN project_user_visibility v ON v.project_id = pc.project_key
                    INNER JOIN user AS u ON u.user_id = v.user_id
                    WHERE u.username IN {anon_et_al}
                    GROUP BY pc.category_key;""".format(anon_et_al = anon_et_al)

        items = {}

        with admin_query() as cursor:
            try:
                cursor.execute(query, username)
                for row in cursor:
                    items[row[0]] = row[1]
            except Exception, e:
                conf.log.exception(
                    "Exception. Projects.get_project_counts_per_category failed with query '''%s'''." %
                    query)

        # Refresh cache
        if items:
            cache.set_project_counts_per_category(username, items)

        return items

    def get_all_user_tasks(self, username, projects):
        """ Get tasks that are assigned or owned by user with 'username' in the
            context of certain projects
        """
        tasks = []

        # Index values (just to keep this understandable :)
        URL = 0
        SUMMARY = 1
        DESCRIPTION = 2
        PRIORITY = 3
        TIME = 4
        PRIORITY_SORT = 5
        from trac.util.datefmt import to_datetime

        # Find tasks for given projects
        for project in projects:
            prjtasks = project.get_user_tasks(username)
            if len(prjtasks) > 0:
                for row in prjtasks:
                    time = row[TIME]
                    if row[TIME] > 9999999999:
                        time = row[TIME] / 1000000

                    new_row = [project, row[URL], row[SUMMARY], row[DESCRIPTION], row[PRIORITY],
                               to_datetime(time), row[PRIORITY_SORT], project.project_name]
                    tasks.append(new_row)
        return tasks

    def get_all_user_task_sums(self, username, projects):
        """ Get task sums that are assigned or owned by user with 'username' in the
            context of certain projects
        """
        total = 0
        closed = 0

        # Find tasks for given projects
        for project in projects:
            (prjtotal, prjclosed) = project.get_user_task_sums(username)
            total = total + prjtotal
            closed = closed + prjclosed

        return total, closed

    def get_projects_for_rss(self, user_id, limit_start, projectcount, query_type):
        """
        Returns the most active/newest/featured projects, if user can see the project.
        Results can be limited by starting index and by how many projects we want to see.

        :param int user_id: The user id for the user as in database.
        :param int limit_start: Index on where to start listing
        :param int projectcount: How many projects to list
        :param str query_type: Type of query (NEWEST/NEWESTFILTERED/MOSTACTIVE/FEATURED)
        :returns: List of project object matching query
        """
        query = None

        if not user_id:
            return []

        if query_type in ["NEWEST", "NEWESTFILTERED"]:
            query = ("SELECT projects.environment_name AS name, projects.description AS description, "
                     "projects.created AS date, projects.project_name, project_icon.content_type AS "
                     "icon_type, length(project_icon.icon_data) AS icon_size FROM `group` "
                     "INNER JOIN user_group ON user_group.group_key = group.group_id "
                     "INNER JOIN projects ON group.trac_environment_key = projects.trac_environment_key "
                     "LEFT JOIN project_icon ON IFNULL(projects.icon_id,%d) = project_icon.icon_id " %
                     safe_int(conf.default_icon_id))
            if conf.use_project_filtering and query_type == "NEWESTFILTERED":
                subq = ("SELECT pd.project_key AS project_key FROM %(database)s.event_fact AS ef "
                        "INNER JOIN %(database)s.project_dim AS pd ON pd.project_sk = ef.project_sk "
                        "GROUP BY ef.project_sk" % {'database': conf.db_analytical_schema_name})
                query += "INNER JOIN (%s) AS tmp ON tmp.project_key = projects.project_id " % subq
            query += ("WHERE user_group.user_key = '%d' GROUP BY group.trac_environment_key "
                      "ORDER BY projects.published DESC,projects.created DESC LIMIT %d,%d" %
                      (safe_int(user_id), safe_int(limit_start), safe_int(projectcount)))
        elif query_type == "MOSTACTIVE":
            query = ("SELECT projects.environment_name AS name, projects.description AS "
                     "description, projects.created AS date, projects.project_name, "
                     "project_icon.content_type AS icon_type, length(project_icon.icon_data) AS "
                     "icon_size FROM `group` INNER JOIN projects ON group.trac_environment_key = "
                     "projects.trac_environment_key INNER JOIN project_activity ON "
                     "project_activity.project_key = projects.project_id INNER JOIN user_group "
                     "ON user_group.group_key = group.group_id LEFT JOIN project_icon ON "
                     "IFNULL(projects.icon_id,%d) = project_icon.icon_id "
                     "WHERE user_group.user_key = '%d' GROUP BY group.trac_environment_key "
                     "ORDER BY (ticket_changes+wiki_changes+scm_changes+attachment_changes+"
                     "discussion_changes) DESC LIMIT %d,%d" %
                     (safe_int(conf.default_icon_id), safe_int(user_id), safe_int(limit_start),
                      safe_int(projectcount)))
        elif query_type == "FEATURED":
            query = ("SELECT projects.environment_name AS name,projects.description AS description, "
                     "projects.created AS date, projects.project_name, project_icon.content_type AS "
                     "icon_type, length(project_icon.icon_data) AS icon_size FROM project_selected "
                     "INNER JOIN projects ON project_selected.project_id = projects.project_id "
                     "LEFT JOIN project_icon ON IFNULL(projects.icon_id,%d) = project_icon.icon_id "
                     "ORDER BY project_selected.value LIMIT %d,%d" %
                     (safe_int(conf.default_icon_id), safe_int(limit_start), safe_int(projectcount)))

        if query:
            return self.__queryProjectsWithDescr(query)

    def search(self, keywords, category_ids, username='anonymous', order_by='newest', sub_page=1, limit=5,
               icon_data=False, all_categories=None):
        """
        Search for projects with fulltext and categories for explore projects.

        .. Note::

            Order by featured is not supported anymore.

        :param order_by: str either 'newest' or 'active'
        :param all_categories: equal to CQDECategoryStore.get_all_categories()
        """
        if not all_categories:
            all_categories = CQDECategoryStore().get_all_categories()

        icon_size = 0
        icon_type = ''

        # this is needed only for generating rss feed on explore projects
        if icon_data:
            sql = ("SELECT IFNULL(LENGTH(icon_data),0), IFNULL (content_type, 'image/png') FROM "
                   "project_icon WHERE icon_id = %s" % safe_int(conf.default_icon_id))

            row = []
            with admin_query() as cursor:
                try:
                    cursor.execute(sql)
                    row = cursor.fetchone()
                except:
                    conf.log.exception("Failed to fetch default project icon")

            if row:
                icon_size = str(row[0])
                icon_type = row[1]

        limit = safe_int(limit)
        limit_attr = {'limit_start': (int(sub_page) - 1) * limit, 'limit': limit}

        wheres = [" u.username IN ('anonymous')"]
        if username != 'anonymous':
            # Alternative implementation by using EXISTS sub query
            wheres = [" u.username IN ('anonymous', '%s')" % safe_string(username)]

        joins = []

        activity_statement = self._activity_statement()

        # Sorting by featured is no longer supported.

        select_columns = """
        DISTINCT p.project_id, p.project_name, p.environment_name, p.description,
        p.author, p.created, p.updated, p.published, p.parent_id, p.icon_id,
        p.trac_environment_key, p.icon_id,
        IFNULL(length(pi.icon_data), 0) AS icon_size, IFNULL(pi.content_type, '') AS icon_type,
        {activity_statement} AS a
        """.format(icon_size=str(icon_size),icon_type=icon_type, activity_statement=activity_statement)

        select_count = """COUNT(DISTINCT p.project_id)"""

        if category_ids:
            # Given categories

            search_cat_list = []
            cat_ids_in_search = set([])
            list_of_or_category_ids = []
            and_category_ids = []

            for cat_id in category_ids:
                if not all_categories.has_key(cat_id):
                    continue
                if cat_id in cat_ids_in_search:
                    continue
                cat_ids_in_search.add(cat_id)
                category = all_categories[cat_id]

                if category.has_children():
                    categories_to_go = []
                    categories_to_go.extend(category.children)
                    current_categories = [cat_id]
                    # Counter for avoiding infinite loops
                    counter = len(all_categories) + 1
                    while categories_to_go and counter > 0:
                        child_cat = categories_to_go.pop()
                        if child_cat.category_id in cat_ids_in_search:
                            # categories are wrong somehow. Should not happen when used properly.
                            continue
                        categories_to_go.extend(child_cat.children)
                        cat_ids_in_search.add(child_cat.category_id)
                        current_categories.append(child_cat.category_id)
                        counter -= 1
                    if counter == 0:
                        conf.log.critical("Infinite loop when searching all sub categories of %s " % cat_id)
                    list_of_or_category_ids.append(current_categories)
                else:
                    and_category_ids.append(cat_id)

            # Important special case when searching with one category:
            if len(and_category_ids) == 1:
                joins += ["INNER JOIN project_categories AS pc ON pc.project_key = p.project_id "]
                wheres += ["pc.category_key = %s" % safe_int(and_category_ids[0])]
            elif and_category_ids:
                # Join id:s into in clause wrapped in quotes
                id_list_str = ', '.join([str(safe_int(id)) for id in and_category_ids])
                wheres += [
                    """
                    p.project_id IN (SELECT project_categories.project_key
                                       FROM project_categories
                                      WHERE category_key IN (%s)
                                   GROUP BY project_key
                                     HAVING COUNT(*) = %s)"""  % (id_list_str, len(and_category_ids))
                ]
            for or_category_ids in list_of_or_category_ids:
                id_list_str = ', '.join([str(safe_int(id)) for id in or_category_ids])
                wheres += [
                    """
                    EXISTS (SELECT project_categories.project_key
                              FROM project_categories
                             WHERE project_key = p.project_id
                               AND category_key IN (%s))"""  % id_list_str
                ]


        if keywords:
            wheres += [
            "CONCAT(p.project_name COLLATE utf8_general_ci,p.environment_name, p.description) LIKE '%{0}%'"
            .format(safe_string(kw.replace('%','\\%'))) for kw in keywords.split() if kw]

        # Merge where statements
        where_str = '\n           AND '.join(wheres)

        # Merge join statements
        join_str = " ".join(joins)

        order_by_str = ""
        if order_by == "active":
            order_by_str = " ORDER BY a DESC "
        elif order_by == "recent":
            order_by_str = " ORDER BY IFNULL(p.published, p.created) DESC "

        left_join_icon = "LEFT JOIN project_icon AS pi ON pi.icon_id = p.icon_id "

        # Note: If project_activity is not calculated, the project will not be shown here!
        query_template = """
        SELECT {select_clause}
        FROM project_user_visibility AS v
        INNER JOIN projects AS p ON p.project_id = v.project_id
        INNER JOIN user AS u ON u.user_id = v.user_id
        INNER JOIN project_activity AS pa ON pa.project_key = p.project_id
        {left_join_icon}
        {join_str}
        WHERE {where_str}
        {order_by}
        {limit}
        """
        # The count_query doesn't have left_join_icon, order_by, and limit parts.
        # Here, if we would form query_template so that it already contained the parts
        # common to both query and count_query, i.e., where_str, join_str, wher_str),
        # there would be possibility to put ' {anything} ' or ' %(anything)s ' into where_str.
        # Thus, safer to do the formatting once for all in both cases.
        query = query_template.format(join_str=join_str, where_str=where_str,
                select_clause=select_columns,left_join_icon=left_join_icon,
                order_by=order_by_str,
                limit= "LIMIT %(limit_start)d, %(limit)d " % limit_attr)
        count_query = query_template.format(join_str=join_str, where_str=where_str,
            select_clause = select_count, left_join_icon = '', order_by = '', limit = '')

        conf.log.debug("Explore projects search query: %s",query)
        conf.log.debug("Explore projects search count_query: %s",count_query)

        query_count = self._get_single_result(count_query) or 0
        projects, activities = self.queryProjectObjectsForSearch(query)
        return projects, activities, query_count

    def search_project(self, keywords, category_ids, sub_page=1, limit=5):
        """ Search for projects with fulltext and categories
        """
        limit = safe_int(limit)
        limit_attr = {'limit_start': (int(sub_page) - 1) * limit, 'limit': limit}

        select = "SELECT DISTINCT p.project_id,p.project_name,p.environment_name,p.description,"\
                 "p.author,p.created,p.updated,p.published,p.parent_id,p.icon_id FROM "\
                 "(SELECT DISTINCT * , CONCAT(project_name COLLATE utf8_general_ci,environment_name, description) as f FROM projects) AS p "

        wheres = []
        joins = []

        if category_ids:
            # Given categories
            search_cat_list = category_ids

            joins += ["INNER JOIN project_categories AS pc ON pc.project_key = p.project_id "]

            # Join id:s into in clause wrapped in quotes
            id_list = ', '.join([str(safe_int(id)) for id in search_cat_list])
            wheres += [" pc.category_key IN (%s)" % id_list]

        if keywords:
            # Escape SQL query. Escape also the special % and _ characters
            wheres += ["f LIKE '%{0}%'".format(safe_string(kw.replace('%', '\%').replace('_', '\_'))) for kw in keywords.split() if kw]

        if len(wheres) > 0:
            # Merge where statements
            where_str = " WHERE " + ' AND '.join(wheres)
        else:
            where_str = ""

        # Merge join statements
        join_str = " ".join(joins)

        attr_str = " ORDER BY IFNULL(p.published, p.created) DESC LIMIT %(limit_start)d, %(limit)d" % limit_attr
        query = select + join_str + where_str + attr_str

        return self.__queryProjectsWithDescr(query)

    def add_public_project_visibility(self, project_id):
        # check if anonymous user exists
        user_store = conf.getUserStore()
        anon = user_store.getUser('anonymous')
        if not anon:
            return

        # add entry to the visibility table if not there yet
        sql = "INSERT IGNORE INTO project_user_visibility VALUES(%s, %s)"
        with admin_transaction() as cursor:
            try:
                cursor.execute(sql, (project_id, anon.id))
            except Exception, e:
                conf.log.exception("Project query failed: {0}".format(sql))

    def remove_public_project_visibility(self, project_id):
        # check if anonymous user exists
        user_store = conf.getUserStore()
        anon = user_store.getUser('anonymous')
        if not anon:
            return

        # remove entry from the visibility table
        sql = "DELETE FROM project_user_visibility WHERE project_id=%s AND user_id=%s LIMIT 1"
        with admin_transaction() as cursor:
            try:
                cursor.execute(sql, (project_id, anon.id))
            except Exception, e:
                conf.log.exception("Project query failed: {0}".format(sql))

    def _get_single_result(self, query):
        value = None
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
                if row:
                    value = row[0]
            except Exception, e:
                conf.log.exception("Project query failed: {0}".format(query))

        return value

    def get_activity_quartals(self):
        """ Return an array of count boundaries for
            activity quartal buckets
        """
        activity_statement = self._activity_statement()

        count_q = """
        SELECT COUNT(DISTINCT {0})
        FROM project_activity AS pa
        """.format(activity_statement)

        # NOTE: limit parameter is set on execute
        activity_q = """
        SELECT DISTINCT {0} AS activity
        FROM project_activity AS pa
        ORDER BY {1} ASC
        LIMIT %d, 1
        """.format(activity_statement, activity_statement)

        bounds = [0, 0, 0, 0]
        with admin_query() as cursor:
            try:
                # Get count
                cursor.execute(count_q)
                quarter = (cursor.fetchone()[0]) / 4
                if quarter:

                    # Get activities
                    cursor.execute(activity_q % math.floor(quarter))
                    fq = cursor.fetchone()[0]

                    cursor.execute(activity_q % math.floor(quarter * 2))
                    sq = cursor.fetchone()[0]

                    cursor.execute(activity_q % math.floor(quarter * 3))
                    tq = cursor.fetchone()[0]

                    bounds = [0, fq, sq, tq]
            except Exception, e:
                conf.log.exception("Failed fetching activity quartals: {0}, {1}".format(count_q, activity_q))
                raise

        return bounds

    def _activity_statement(self):
        """
        Returns SQL statement calculating project activity. In the statement, pa corresponds to project_activity.
        """
        order_by = "(pa.ticket_changes+pa.wiki_changes+pa.scm_changes+pa.attachment_changes+pa.discussion_changes)"
        return order_by

    def __queryProjects(self, project_query):
        """ Method that queries projects using given query and then wraps them
            into dictionary

            Used with project list
        """
        projects = []
        with admin_query() as cursor:
            try:
                cursor.execute(project_query)
                for project in cursor:
                    author = project[Project.FIELD_COUNT]
                    if len(project) > Project.FIELD_COUNT and conf.expose_user_identity:
                        # Given name is at Project.FIELD_COUNT + 1
                        author = project[Project.FIELD_COUNT + 1] or _('(invalid given name)')
                        if len(project) > Project.FIELD_COUNT + 1:
                            # Last name is at Project.F
                            author += " " + (project[Project.FIELD_COUNT + 2] or _('(invalid last name)'))

                    # FIXME: description is project_name and name is env_name
                    projects.append({'description': project[1],
                                     'name': project[2],
                                     'author': author,
                                     'date': project[5],
                                     'updated': project[6],
                                     'published': project[7],
                                     'icon_id': project[9]
                    })
            except:
                conf.log.exception("Project query failed: {0}".format(project_query))
                raise

        return projects

    def __queryProjectsWithDescr(self, project_query):
        """ Method that queries projects using given query and then wraps them
            into dictionary. This version adds also the real description field

            Used with project list
        """
        projects = []
        with admin_query(cursors.DictCursor) as cursor:
            try:
                cursor.execute(project_query)
                projects = cursor.fetchall()
            except:
                conf.log.exception("Project query failed: {0}".format(project_query))
                raise

        return projects

    def queryProjectObjects(self, project_query):
        projects = []

        with admin_query() as cursor:
            try:
                cursor.execute(project_query)
                for project in cursor:
                    projects.append(Projects.sqlToProject(project))
            except:
                conf.log.exception("Project query failed: {0}".format(project_query))
                raise

        return projects

    def queryProjectObjectsForSearch(self, project_query):
        projects = []
        activities = {}
        with admin_query() as cursor:
            try:
                cursor.execute(project_query)
                for project in cursor:
                    projects.append(Projects.sqlToProject(project))
                    activities[project[0]] = project[-1]
            except:
                conf.log.exception("Project query failed: {0}".format(project_query))
                raise

        return projects, activities

    def queryProjectObjectsWithUsers(self, project_query):

        projects = []
        with admin_query() as cursor:
            try:
                cursor.execute(project_query)
                for project in cursor:
                    projects.append(Projects.sqlToProject(project[:Project.FIELD_COUNT]))
            except:
                conf.log.exception("Project query failed: {0}".format(project_query))
                raise

        return projects

    @staticmethod
    def sqlToProject(project_data, parent_data=None):
        author = None
        parent = None

        if parent_data:
            parent = Projects.sqlToProject(parent_data)

        prj = Project(
            id=project_data[0],
            project_name=project_data[1],
            env_name=project_data[2],
            description=project_data[3],
            author_id=project_data[4],
            created=project_data[5],
            updated=project_data[6],
            published=project_data[7],
            parent_id=project_data[8],
            icon_id=project_data[9],
            trac_environment_key=project_data[10],
        )

        if len(project_data) >= 14:
            prj.icon_type = project_data[14]
            prj.icon_size = project_data[13]
            conf.log.debug("type set")
        return prj

    def getEnabledServices(self, environment):
        """
            Create service list from checking system properties
        """

        # Forced services
        services = ['versioncontrol|svn|false|Subversion', 'documenting|wiki|true|Wiki',
                    'tasks|trac|true|Task management system']

        modules = {
            'gitconnector': 'versioncontrol|git|false|GIT',
            'mercurialconnector': 'versioncontrol|hg|false|Mercurial',
            'bzrconnector': 'versioncontrol|bzr|false|Bazaar',
            'cvsconnector': 'versioncontrol|cvs|false|Concurrent Versions System',
            'perforceconnector': 'versioncontrol|perforce|Perforce',
            'clearcaseconnector': 'versioncontrol|clearcase|ClearCase'
        }

        # Add available services
        from trac.core import ComponentMeta

        for component in ComponentMeta._components:
            modname = component.__name__.lower()
            if environment.is_component_enabled(component):
                if modules.has_key(modname):
                    services.append(modules[modname])

        return services

    def getServices(self, store, service_list):
        store['services'] = {}
        vctypes = {
            'versioncontrol|svn': 'svn',
            'versioncontrol|subversion': 'svn',
            'subversion': 'svn',
            'svn': 'svn',
            'versioncontrol|git': 'git',
            'git': 'git',
            'versioncontrol|hg': 'hg',
            'versioncontrol|mercurial': 'hg',
            'mercurial': 'hg',
            'hg': 'hg',
            'versioncontrol|bzr': 'bzr',
            'versioncontrol|bazaar': 'bzr',
            'bzr': 'bzr',
            'versioncontrol|cvs': 'cvs',
            'cvs': 'cvs',
            'versioncontrol|perforce': 'perforce',
            'perforce': 'perforce',
            'versioncontrol|clearcase': 'clearcase',
            'clearcase': 'clearcase'
        }

        othertypes = {
            'documenting|wiki': 'wiki',
            'wiki': 'wiki',
            'tasks|trac': 'trac',
            'trac': 'trac',
            'faults|bugzilla': 'bugzilla',
            'bugzilla': 'bugzilla',
            'release|cruisecontrol': 'cc',
            'cruisecontrol': 'cc',
            'messaging|jabber': 'jabber',
            'jabber': 'jabber',
            'messaging|irc': 'irc',
            'irc': 'irc',
            'forum': 'forum',
            'news|news': 'news',
            'news': 'news',
            'news|blog': 'blog',
            'blog': 'blog'
        }

        for service in service_list.split(','):
            service = service.lower().strip()
            if vctypes.has_key(service):
                store['vcs_type'] = vctypes[service]
                store['vcs_settings'] = {}
            elif othertypes.has_key(service):
                store['services'][othertypes[service]] = {}

        return store

    # FIXME: Maybe create another class for StorageNotifications?
    def get_storage_info(self):
        rootpath = conf.sys_root
        api = ProjectsInfo()
        info = api.disk_free(rootpath)
        info[0] = rootpath
        return info

    # FIXME: Maybe create another class for StorageNotifications?
    def get_storage_csv_modification_time(self):
        api = ProjectsInfo()
        filename = conf.generated_content_dir + "/" + conf.storage_usage
        return time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime(api.file_modified(filename)))

    # FIXME: Should be private helper method
    def is_week_gone(self, today, lastsend):
        if (today - long(lastsend)) < 604800: # week in seconds
            return False
        else:
            return True

    # FIXME: Maybe create another class for StorageNotifications?
    def get_notified_projects(self):

        projects = {}
        errorlimit = long(conf.storage_locking_limit)
        today = long(time.time())
        notificationfile = conf.generated_content_dir + "/" + conf.notifications_file
        storageusagefile = conf.generated_content_dir + "/" + conf.storage_usage
        try:
            readnew = csv.reader(open(storageusagefile, "rb"))
            for row in readnew:
                if len(row) >= 4:
                    total = long(row[1]) + long(row[2]) + long(row[3])
                    if total > errorlimit > 0:
                        projects[row[0]] = ProjectNotifications(today, total, True)
        except Exception, e:
            conf.log.exception("Failed the read projects storage information")

        try:
            readold = csv.reader(open(notificationfile, "rb"))
            for row in readold:
                if len(row) >= 2:
                    if projects[row[0]]:
                        projects[row[0]].notifynow = self.is_week_gone(today, row[1])
                        if projects[row[0]].notifynow:
                            projects[row[0]].notifytime = today
                        else:
                            projects[row[0]].notifytime = row[1]
        except Exception, e:
            conf.log.exception("Failed the read notification times from file")

        try:
            writer = csv.writer(open(notificationfile, 'w'),
                delimiter='\n', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([s.encode("utf-8") + "," + str(projects[s].notifytime) for s in projects.keys()])
        except Exception, e:
            conf.log.exception("Failed the write notification times to file")

        return projects

    # FIXME: Should be private method and probably in somewhere else
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
