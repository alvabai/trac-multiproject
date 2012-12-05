# -*- coding: utf-8 -*-
"""
Module implements the DAO objects for Project and specialized HomeProject
"""
import tempfile
import os
import re

from trac.core import TracError
from trac.env import open_environment
import Image

from multiproject.core.cache.project_cache import ProjectCache
from multiproject.core.configuration import conf
from multiproject.core.db import admin_query, admin_transaction, safe_string, safe_int
from multiproject.core.files.files_conf import FilesConfiguration
from multiproject.core.users import User, get_userstore
from multiproject.core.exceptions import ProjectValidationException
from multiproject.core.permissions import CQDEUserGroupStore, CQDEPermissionStore


class Project(object):
    """
    Project provides a mapping between database and object.
    Example usage::

    >>> author = userstore.getUserWhereId(123)
    >>> p = Project(id=12, env_name='projectx', project_name='Project X', author_id=author.id)
    >>> p.save()
    >>>
    >>> # Modify values
    >>> p.author = userstore.getUserWhereId(124)
    >>> p.save()

    """
    # TODO: ORM, anyone?
    # Mapping property:dbcolumn
    FIELDS = {
        'id': 'project_id',
        'project_name': 'project_name',
        'env_name': 'environment_name',
        'description': 'description',
        'author_id': 'author',
        'created': 'created',
        'updated': 'updated',
        'published': 'published',
        'parent_id': 'parent_id',
        'icon_id': 'icon_id',
        'trac_environment_key': 'trac_environment_key',
    }
    FIELD_COUNT = len(FIELDS)

    def __init__(self, id, env_name, project_name, description, author_id, created, trac_environment_key=None,
                 updated=None, published=None, parent_id=None,
                 discforum=False, icon_id=None):

        # Private attributes for properties
        self._parent_project = None
        self._author = None
        self.description = description

        # NOTE: id is None when new project is created
        self.id = int(id) if id else None
        self.env_name = env_name
        self.project_name = project_name
        self.created = created
        self.author_id = int(author_id)
        self.parent_id = int(parent_id) if parent_id else None

        # Only None in case project is not recorded into database yet.
        # Avoid using, migrate to `self.id` everywhere.
        self.trac_environment_key = trac_environment_key

        self.updated = updated
        self.published = published
        self.discforum = discforum
        self.icon_id = icon_id
        self.icon_type = ""
        self.icon_size = 0

    @staticmethod
    def get(env=None, id=None, env_name=None, use_cache=True):
        """
        Factory method for getting Project instance by some known value.
        Always prefer `env` if possible as it should be most available and easiest.

        :param env: Preferred method. Instantiate by Trac Environment.
        :param id: Instantiate by project id.
        :param env_name: Instantiate by env_name.
        :param use_cache: Whether to use internal project cache.
        :return: Project class instance.
        :raises: TracError if asked unknown project with `env_name` (legacy)
        """
        args = [id, env_name, env]
        if len(args) - args.count(None) != 1:
            raise ValueError('Invalid number of arguments (env=%s, id=%s, env_name=%s)' % (env, id, env_name))

        if env_name:
            project = Project._get_project(env_name=env_name, use_cache=False)
            # To comply with previous functionality, raise TracError
            if not project:
                raise TracError('Trac environment cannot be found')
            return project
        elif id:
            return Project._get_project(project_id=id, use_cache=use_cache)
        else:  # env
            try:
                env_name = env.project_identifier
            except AttributeError:
                env_name = env.path.split('/')[-1]
            return Project._get_project(env_name=env_name, use_cache=use_cache)

    @staticmethod
    def _get_project(project_id=None, env_name=None, use_cache=True):
        by_env = False
        if env_name:
            if env_name == conf.sys_home_project_name:
                # TODO: eventually we want to have home project in projects table ...
                raise NotImplementedError('home project not supported')
            by_env = True
            param = env_name
        elif project_id:
            if not project_id:
                return None
            param = project_id
        else:
            return None

        cache = ProjectCache.instance()
        # Try cache
        if use_cache:
            if by_env:
                project = cache.get_project_by_env_name(env_name)
            else:
                project = cache.getProject(project_id)
            if project:
                return project

        query = ("SELECT project_id, environment_name, project_name, description, author, created, updated, "
                 "published, parent_id, icon_id, trac_environment_key "
                 "FROM projects WHERE {0} = %s".format('environment_name' if by_env else 'project_id'))

        try:
            with admin_query() as cursor:
                cursor.execute(query, param)
                row = cursor.fetchone()
                if not row:
                    return None
                project = Project(
                    id=row[0],
                    env_name=row[1],
                    project_name=row[2],
                    description=row[3],
                    author_id=row[4],
                    created=row[5],
                    updated=row[6],
                    published=row[7],
                    parent_id=row[8],
                    icon_id=row[9],
                    trac_environment_key=row[10],
                )
            if use_cache:
                if by_env:
                    cache.set_project_by_env_name(env_name, project)
                else:
                    cache.setProject(project)

            return project
        except Exception as e:
            conf.log.exception("Exception occurred while running query: '''%s'''" % query)
            return None

    @property
    def project_name(self):
        """
        Property for getting project name
        """
        return self._name.decode('utf-8')

    @project_name.setter
    def project_name(self, value):
        """
        Property for setting project name
        """
        assert len(value) >= 2, 'Project name needs to be at least 2 characters long'
        self._name = value.encode('utf-8')

    @property
    def author(self):
        """
        Property for getting project author

        :returns: User instance of the project author
        """
        if self._author:
            return self._author

        userstore = get_userstore()
        self._author = userstore.getUserWhereId(self.author_id)

        return self._author

    @author.setter
    def author(self, author):
        """
        Sets/updates the author

        :param User author: Project author to set for the project
        """
        assert isinstance(author, User), 'Author needs to be set and User instance'
        self._author = author
        self.author_id = author.id

    @property
    def parent_project(self):
        """
        Property for getting parent project

        :returns: User instance of the parent project. If not set, returns None
        """
        if self._parent_project:
            return self._parent_project
        if self.parent_id is None:
            return None
        self._parent_project = Project.get(id=self.parent_id)
        return self._parent_project

    @parent_project.setter
    def parent_project(self, project):
        """
        Sets/updates the parent project: the project where the current if cloned from

        :param Project project: Project author to set for the project
        """
        assert isinstance(project, User), 'Author needs to be set and User instance'
        self._parent_project = project
        self.parent_id = project.id

    @property
    def icon_url(self):
        """
        Returns the URL path to project icon, or default if not set
        :return: Path of the icon URL
        """
        icon_default_url = conf.get('multiproject-projects', 'icon_default_url', '')

        return icon_default_url


    def save(self):
        """
        Saves the changes set to properties into database

        >>> p = Project()
        >>> p.author = newauthor
        >>> p.save()

        """
        # Ensure the data is validated
        self.validate()

        # Construct SQL update statement using db fields and setting %s placeholder for values
        sql = '''
        UPDATE projects
        SET {0}
        WHERE project_id = %s
        '''.format(', '.join(['{0}=%s'.format(field) for field in self.FIELDS.values()]))

        with admin_transaction() as cursor:
            cursor.execute(sql, ([getattr(self, pro) for pro in self.FIELDS.keys()] + [self.id]))

        # Clear the project cache
        cache = ProjectCache.instance()
        cache.clear_project(self)

        conf.log.info('Saved project {0} changes into database'.format(self))

    def get_env(self):
        """
        Returns Trac environment for the project in question
        Example usage::

            from trac.perm import PermissionCache
            from multiproject.common.projects import Project

            project = Project.get(id=123)

            # Check permission from project env
            prjperm = PermissionCache(project.get_env(), req.authname)
            prjperm.require('ACTION')

        .. NOTE::

            For special home project, one can request the env directly
            from the HomeProject class::

                from multiproject.common.projects import HomeProject
                homeenv = HomeProject().get_env()

        """
        return open_environment(os.path.join(conf.sys_projects_root, self.env_name), use_cache=True)

    def get_repository_url(self, relative=False):
        # TODO: Find way to fix this
        """
        WARNING: Expensive call due conf.getVersionControlType
        """
        params = {'domain': conf.domain_name,
                  'project': self.env_name,
                  'path': conf.getVersionControlType(self.env_name),
                  'scheme': conf.default_http_scheme}

        if relative:
            return "%(path)s/%(project)s/" % params
        else:
            return "%(scheme)s://%(domain)s/%(path)s/%(project)s/" % params

    def get_dav_url(self, relative=False):
        path = '/'.join([conf.url_projects_path,
                         FilesConfiguration().url_dav_path,
                         self.env_name, ''])
        if relative:
            return path
        params = {'domain': conf.domain_name,
                  'scheme': conf.default_http_scheme,
                  'path': path}
        return "%(scheme)s://%(domain)s%(path)s" % params

    def get_url(self, relative=False):
        prj_path = conf.url_projects_path

        if prj_path is None:
            prj_path = ''

        params = {'domain': conf.domain_name,
                  'project': self.env_name,
                  'path': prj_path,
                  'scheme': conf.default_http_scheme}

        if relative:
            return "%(path)s/%(project)s/" % params
        else:
            return "%(scheme)s://%(domain)s%(path)s/%(project)s/" % params

    def get_team(self):
        """ Returns a list of those users that have rights to project
        """
        query = ("SELECT DISTINCT user.* FROM user "
                 "INNER JOIN user_group ON user.user_id = user_group.user_key "
                 "INNER JOIN `group` ON user_group.group_key = group.group_id "
                 "WHERE group.trac_environment_key = %d "
                 "AND user.username NOT IN('anonymous', 'authenticated')" %
                 safe_int(self.trac_environment_key))

        userstore = get_userstore()
        return userstore.query_users(query)

    def is_admin(self, username):
        """
        Check if user is TRAC_ADMIN on this project
        """
        query = ("SELECT 1 FROM action a, group_permission gp, `group` g, projects p, user_group ug, user u "
                 "WHERE gp.group_key = g.group_id AND g.trac_environment_key = p.trac_environment_key AND "
                 "p.trac_environment_key = %s AND gp.permission_key = a.action_id "
                 "AND a.action_string = 'TRAC_ADMIN' AND ug.user_key = u.user_id AND ug.group_key = g.group_id "
                 "AND u.username = %s")

        with admin_query() as cursor:
            try:
                cursor.execute(query, (self.trac_environment_key, username))
                if cursor.fetchall():
                    return True
            except:
                conf.log.exception("Exception. Project.is_admin query failed. '''%s'''" % query)
                raise

        return False

    @property
    def public(self):
        """
        Check the project visibility

        :returns: True if project is considered public (wide permissions), otherwise False
        """
        groupstore = CQDEUserGroupStore(self.trac_environment_key)
        return groupstore.is_public_project()

    def get_team_email_addresses(self):
        users = []
        for user in self.get_team():
            users.append(user.username)
        return get_userstore().get_emails(users)

    def get_admin_email_addresses(self):
        admins = CQDEPermissionStore(self.trac_environment_key).get_users_with_permissions(['TRAC_ADMIN'])
        return get_userstore().get_emails(admins)

    def get_email_addess(self, user):
        username = [user]
        return get_userstore().get_emails(username)

    def validate(self):
        """ Validates data given from web form
        """
        self.env_name = self.env_name.strip()

        if re.search('\W', self.env_name):
            raise ProjectValidationException(
                "Only alphanumeric ASCII characters and underscore are allowed in the Identifier field")

        if len(self.env_name.strip('_')) != len(self.env_name):
            raise ProjectValidationException(
                "Identifier can not start or end with underscore. Only allowed in the middle.")

        try:
            self.env_name.decode('ascii')
        except:
            raise ProjectValidationException(
                "Only alphanumeric ASCII characters and underscore are allowed in the Identifier field")

        # It should not be a security/technical issue even if some of the following identifier is tried to be used
        # Anyway make sure that none of these names is used in project to make absolutely sure that
        forbidden_env_names = ['mysql', # db names are not allowed
                               'information_schema',
                               conf.db_admin_schema_name,
                               conf.db_analytical_schema_name,
                               'home',

                               'svn', # scm names are not allowed
                               FilesConfiguration().url_dav_path,
                               'git',
                               'bazaar',
                               'bzr',
                               'perforce',
                               'hg',

                               'htdocs', # static resource location names are not allowed
                               'css',
                               'js',
                               'images',

                               'trac'] # trac is not allowed

        if self.env_name in forbidden_env_names:
            msg = ("Project identifier forbidden. Try something else. "
                   "TIP: Identifier is case sensitive. You can try changing letter casing.")
            raise ProjectValidationException(msg)

        if len(self.env_name) < 1:
            raise ProjectValidationException("Too short project identifier. Should be at least one character.")

        if len(self.env_name) > 32:
            raise ProjectValidationException("Too long project identifier. Length can be 32 characters at most.")

        if len(self.description) < 8:
            raise ProjectValidationException("Too short description.")

        if len(self.project_name) < 2:
            raise ProjectValidationException("Too short project name. Should be at least two characters.")

        if len(self.project_name) > 64:
            raise ProjectValidationException("Too long project name. Length can be 64 characters at most.")

        if not re.search(r"^[a-zA-Z0-9., ?!&_:/()\[\]{}-]*$", self.project_name):
            raise ProjectValidationException(
                "The name field may only contain the following characters: a-Z, 0-9, '.', ',', ' ', '-', '_', ?', '!', '&', ':', (), [] and {}")

    @property
    def trac_fs_path(self):
        return os.path.join(conf.sys_projects_root, self.env_name)

    @property
    def vcs_fs_path(self):
        return os.path.join(conf.sys_vcs_root, self.env_name)

    @property
    def dav_fs_path(self):
        return os.path.join(FilesConfiguration().sys_dav_root, self.env_name)

    def get_child_projects(self):
        """ Returns projects that have repository of this project
        """
        from multiproject.common.projects import Projects

        query = "SELECT * FROM projects WHERE parent_id = %d" % safe_int(self.id)
        api = Projects()

        return api.queryProjectObjects(query)

    def refresh(self):
        """ Reads all project data from database back
        """
        if self.id:
            project = Project.get(id=self.id)
        else:
            project = Project.get(env_name=self.env_name)

        if project is None:
            conf.log.warning('Project cannot be found')
            return

        self.id = project.id
        self.env_name = project.env_name
        self.project_name = project.project_name
        self.description = project.description
        self.author_id = project.author_id
        self.created = project.created
        self.parent_id = project.parent_id
        self.discforum = project.discforum
        self.icon_id = project.icon_id
        self.trac_environment_key = project.trac_environment_key

        if project.parent_project:
            self.parent_project = project.parent_project

        if project._author:
            self._author = project._author

    def get_user_tasks(self, username):
        """
        Method for querying users tasks in a specific project context

        Gives url to ticket and it's summary
        """
        env_url = conf.getEnvironmentUrl(self.env_name) + "/ticket/"

        # Base query
        query = ("SELECT concat('%(env_url)s', tc.id) AS url, tc.summary, tc.description, tc.priority, tc.time, "
                 "`enum`.`value` FROM `%(project)s`.ticket AS tc "
                 "INNER JOIN `%(project)s`.`enum` ON `enum`.`name` = tc.priority AND `enum`.`type` = 'priority' "
                 "WHERE tc.owner = '%(user)s' AND tc.status <> 'closed'" %
                 {'project': self.env_name,
                  'env_url': safe_string(env_url),
                  'user': safe_string(username)})

        # Retrieve data
        rows = []
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
            except:
                conf.log.exception("Exception. Project.get_user_tasks query failed. '''%s'''" % query)

        return rows

    def get_user_task_sums(self, username):
        """ Method for querying user task sums (total tickets and closed tickets)
        """

        # Build query
        query = ("SELECT tc.status, COUNT(*) "
                 "FROM `{0}`.ticket AS tc "
                 "WHERE tc.owner = %s "
                 "GROUP BY tc.status").format(safe_string(self.env_name))

        # Retrieve data
        rows = []
        with admin_query() as cursor:
            try:
                cursor.execute(query, username)
                rows = cursor.fetchall()
            except:
                conf.log.exception("Exception. Project.get_user_task_sums query failed. '''%s'''" % query)

        # go through tasks
        total = 0
        closed = 0
        for row in rows:
            if row[0] == 'closed':
                closed = row[1]
            total += row[1]

        return total, closed

    def createIcon(self, icon):
        """
        Creates icon for user based on icon sent on create form
        """
        if icon is None:
            with admin_transaction() as cursor:
                if self.icon_id is not None:
                    cursor.execute("DELETE FROM project_icon WHERE icon_id = %s", (self.icon_id,))

                cursor.execute("UPDATE projects SET icon_id = NULL WHERE project_id = %s", (self.id,))
                self.icon_id = None
            return

        if isinstance(icon, unicode) or not icon.filename:
            conf.log.warning('Missing image')
            return

        content_type = icon.type
        rs_image_value = None

        # Always resize image to 64x64
        with tempfile.NamedTemporaryFile() as tmp_orgimg:
            tmp_orgimg.write(icon.value)
            # Reel back to beginning after write
            tmp_orgimg.seek(0)
            img = Image.open(tmp_orgimg)
            img.thumbnail((64, 64), Image.ANTIALIAS)

            # NOTE: Is there a way to read file without saving it first?
            with tempfile.NamedTemporaryFile() as tmp_modimg:
                img.save(tmp_modimg, "PNG")
                tmp_modimg.seek(0)
                rs_image_value = tmp_modimg.read()

        # Write image to database
        with admin_transaction() as cursor:
            try:
                # delete old icon from project_icon
                if self.icon_id is not None:
                    cursor.execute("DELETE FROM project_icon WHERE icon_id = %s", (self.icon_id,))
                    # insert new icon into project_icon

                # refactoring needed
                if rs_image_value:
                    query = "INSERT INTO project_icon VALUES(NULL, %s, %s)"
                    cursor.execute(query, (rs_image_value, content_type))
                else:
                    query = "INSERT INTO project_icon VALUES(NULL, %s, %s)"
                    cursor.execute(query, (icon.value, content_type))

                # Resolve last inserted icon id
                cursor.execute("SELECT last_insert_id() FROM project_icon")
                row = cursor.fetchone()
                # If nonzero is returned, row was successfully added.
                self.icon = row[0]
                # update project to correct icon_id
                query = "UPDATE projects SET icon_id = %s WHERE project_id = %s"
                cursor.execute(query, (row[0], self.id))
            except:
                conf.log.exception("Failed to create project icon")
                raise

    def __str__(self):
        """
        Returns short but descriptive information about the project
        """
        # Read object attributes and properties
        pros = self.__dict__
        pros.update({'project_name': self.project_name})
        return '<Project %(id)s: %(project_name)s(%(env_name)s)>' % pros


class HomeProject(object):
    """
    Internal
    """
    def get_users_with_permission(self, permission=None):
        raise NotImplementedError('Getting permission')

    def get_team_email_addresses(self):
        recipients = self.get_users_with_permission()
        return get_userstore().get_emails(recipients)

    def get_admin_email_addresses(self):
        return get_userstore().get_emails(self.get_users_with_permission('TRAC_ADMIN'))

    def get_email_addess(self, user):
        username = [ user ]
        return get_userstore().get_emails(username)

    def get_env(self):
        """
        Returns Trac environment for home project.
        Example usage::

            from trac.env import open_environment
            from trac.perm import PermissionCache
            from multiproject.common.projects import HomeProject

            home = HomeProject().get_env()

            # Check permission from home env
            homeperm = PermissionCache(home, req.authname)
            homeperm.require('ACTION')

        """
        return open_environment(os.path.join(conf.sys_projects_root, conf.sys_home_project_name), use_cache=True)


class ProjectSizeTemplate(object):
    """
    Internal
    """
    def __init__(self, total_space, project_name, project_space, repo_space, dav_space, state):
        self.total_space = total_space
        self.project_name = project_name
        self.project_space = project_space
        self.repo_space = repo_space
        self.dav_space = dav_space
        self.state = state

class ProjectNotifications(object):
    """
    Internal
    """
    def __init__(self, notifytime, totalsize, notifynow):
        self.notifytime = notifytime
        self.totalsize = totalsize
        self.notifynow = notifynow
