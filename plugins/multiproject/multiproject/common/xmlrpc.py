# -*- coding: utf-8 -*-
import os
import exceptions
from datetime import datetime

from trac.core import Component, implements
from trac.versioncontrol import RepositoryManager
from tracrpc.api import IXMLRPCHandler

from multiproject.common.projects import Project, Projects
from multiproject.core.configuration import Configuration
conf = Configuration.instance()
from multiproject.core.categories import CQDECategoryStore
from multiproject.core.multiproj_exceptions import ProjectValidationException
from multiproject.core.users import get_userstore


class UserRPC(Component):
    """ An interface to Trac's user features.
    """

    implements(IXMLRPCHandler)

    def xmlrpc_namespace(self):
        return 'user'

    def xmlrpc_methods(self):
        yield ('', ((int,),), self.authorizationCheck)

    def authorizationCheck(self, req):
        """ Returns authentication confirmation.

            Returns magic number (1038) if user is authenticated. Otherwise
            returns some kind of authentication error.
        """
        return 1038


class ProjectsRPC(Component):
    """ An interface to Trac's projects settings.
    """

    implements(IXMLRPCHandler)

    def _getfiles(self, req, files, repository, path, rev=None):

        node = repository.get_node(path, rev)

        # Entries metadata
        class entry(object):
            __slots__ = 'name rev kind isdir path content_length'.split()

            def __init__(self, node):
                for f in entry.__slots__:
                    setattr(self, f, getattr(node, f))

        entries = [entry(n) for n in node.get_entries()]

        for entry in entries:
            if entry.isdir:
                spath = path + entry.name
                self._getfiles(req, files, repository, spath + "/", rev)
            else:
                files.append(str(path + entry.name))

    def xmlrpc_namespace(self):
        return 'projects'

    def xmlrpc_methods(self):
        yield ('XML_RPC', ((int,),), self.getCount)
        yield ('XML_RPC', ((list,),), self.getProjectCategories)
        yield ('XML_RPC', ((list, str, str),), self.searchProjects)
        yield ('XML_RPC', ((int, str, str),), self.joinProject)
        yield ('XML_RPC', ((list, str, str, str),), self.openProject)
        yield ('XML_RPC', ((str, str, str, str, str, str),), self.createProject)
        yield ('XML_RPC', ((list,),), self.getTracServices)
        yield ('XML_RPC', ((bool, str),), self.projectExists)

    def getCount(self, req):
        """ Returns project count from server
        """
        prjs = Projects()
        return prjs.project_count()

    def getProjectCategories(self, req):
        """ Returns projects categorizations
        """
        categorylist = []

        store = CQDECategoryStore()

        for context in store.get_contexts():
            contextcategories = []
            categories = store.get_categories(context.context_id)
            for category in categories:
                contextcategories.append(category.name)
            categorylist.append(context.name)
            categorylist.append(contextcategories)

        return categorylist

    def openProject(self, req, projectname, revision, extensionlist):
        """ Returns project's connection string and repository file list matched to search criteria.
        """
        # Return values
        if str(projectname).strip() == '':
            e = exceptions.Exception
            raise e("Incorrect project name")

        if revision.strip() == '':
            revision = None
        if extensionlist.strip() == '':
            extensionlist = None

        # Find node for the requested path/rev
        repomgr = RepositoryManager(self.env)
        repository = repomgr.get_repository(None)
        projectname = conf.cleanupProjectName(projectname)
        parts = []

        project = Project.get(env_name=projectname)
        if project:
            parts.append(self.get_scm_repository_url(project.env_name))
        else:
            return []

        try:
            if revision:
                revision = repository.normalize_rev(revision)
            rev_or_latest = revision or repository.youngest_rev

            getfiles = []
            self._getfiles(req, getfiles, repository, '', rev_or_latest)

            if extensionlist:
                extensions = extensionlist.split(',')
                searchresult = []
                for file in getfiles:
                    extension = os.path.splitext(str(file))[1].strip('.')
                    if extension in extensions:
                        searchresult.append(file)
                addfiles = ",".join(searchresult)
            else:
                addfiles = ",".join(getfiles)

            if addfiles:
                # Append version control files
                parts.append('versioncontrolfiles|' + addfiles)
        except Exception:
            self.log.exception("ProjectsRPC.openProject failed")
        return parts

    def searchProjects(self, req, namelike, categories):
        """ Returns project list, what user owns or have access to
        """
        namelike = namelike.strip()

        if namelike == '' or namelike == '*' or namelike is None:
            namelike = None
        else:
            namelike = namelike.replace('%', '\%')
            namelike = namelike.replace('_', '\_')
            namelike = namelike.replace('\\', '\\\\')

        if categories == '':
            categories = None

        myprojects = Projects().get_projects_with_params(req.authname, "VERSION_CONTROL_VIEW",
                                                         namelike, categories)

        projectlist = []
        for project in myprojects:
            projectlist.append(project.env_name + '|' + project.project_name)
        return projectlist

    def joinProject(self, req, projectname, reason):
        """ Request to join to project
        """
        return 0

    def projectExists(self, req, short_name):
        """ Returns True / False depending if project exists
        """
        prjs = Projects()
        return prjs.project_environment_exists(short_name)

    def createProject(self, req, projectid, projectname, description, project_visibility, serviceslist):
        """ Request to create a new project
        """
        services = {}

        if str(projectid).strip() == '':
            e = exceptions.Exception
            raise e("Incorrect project identification name")

        if str(projectname).strip() == '':
            e = exceptions.Exception
            raise e("Incorrect project name")

        users = get_userstore()
        author = users.getUser(req.authname)

        if not author.can_create_project():
            raise Exception("You are not allowed to create projects")
        
        public = False
        published = None
        if project_visibility == "on" or project_visibility == "true":
            public = True
            published = datetime.now()

        # Create project class
        project = Project(id=None,
                          env_name=unicode(projectid),
                          project_name=projectname,
                          description=description,
                          author_id=author.id,
                          created=None,
                          public=public,
                          published=published)

        if project_visibility == "on" or project_visibility == "true":
            services['project_visibility'] = 'on'
        else:
            services['project_visibility'] = 'off'

        projects = Projects()
        projects.getServices(services, serviceslist)

        # Create project
        try:
            projects.create_project(project, services)
            return self.get_scm_repository_url(project.env_name)
        except ProjectValidationException as exc:
            raise Exception(exc.value)
        except:
            raise Exception("Creating project failed. Try again later.")

    def getTracServices(self, req):
        """ Returns available services
        """
        prjs = Projects()
        return prjs.getEnabledServices(self.env)

    def get_scm_repository_url(self, env_name):
        """
        .. WARNING:: Expensive call due conf.getVersionControlType
        """

        vcs = conf.getVersionControlType(env_name)

        if vcs == "git":
            extension = ".git"
        else:
            extension = ""

        params = {'domain': conf.domain_name,
                  'project': env_name,
                  'scm_type': vcs,
                  'scheme': conf.default_http_scheme,
                  'ext': extension}

        return "versioncontrol|%(scm_type)s|%(scheme)s://%(domain)s/%(scm_type)s/%(project)s%(ext)s" % params
