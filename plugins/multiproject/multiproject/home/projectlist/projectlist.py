# -*- coding: utf-8 -*-
import sys, math, re
import os
from pkg_resources import resource_filename
from datetime import datetime

from trac.core import Component, implements, TracError, ExtensionPoint
from trac.perm import PermissionError, IPermissionRequestor
from trac.web import IRequestHandler
from trac.web.chrome import ITemplateProvider, add_warning, add_notice
from trac.web.href import Href
from trac.web.chrome import _

from multiproject.core.users import User, get_userstore
from multiproject.core.util import sanitize_html, safe_address
from multiproject.core.util.request import get_context
from multiproject.core.configuration import conf
from multiproject.core.permissions import CQDEPermissionPolicy
from multiproject.core.exceptions import ProjectValidationException
from multiproject.common.projects import Project, Projects
from multiproject.common.projects.listeners import IProjectChangeListener
from multiproject.common.projects.archive import ProjectArchive


class ProjectListModule(Component):
    """ Trac component for listing/creating projects on web
    """
    implements(ITemplateProvider, IRequestHandler, IPermissionRequestor)
    project_listings = ("recent_public", "active_public")
    home = Href(conf.url_home_path)
    url = Href(os.path.join(conf.url_home_path, 'project'))

    # Extension points
    project_change_listeners = ExtensionPoint(IProjectChangeListener)

    def get_permission_actions(self):
        """ CREATE_PROJECT    : Need's to have this for creating new projects
            LIST_ALL_PROJECTS : Can see all projects in lists (private/public)
        """
        # TODO: Rename to be consistent with other permissions: PROJECT_*
        return ['CREATE_PROJECT', 'LIST_ALL_PROJECTS']

    def match_request(self, req):
        """ Path used for showing this page
        """
        return re.match(r'/project(?:_trac)?(?:/.*)?$', req.path_info) and not req.path_info.startswith('/project/explore')

    def process_request(self, req):
        """ Process request for listing, creating and removing projects
        """
        users = get_userstore()
        ctx = get_context(req)
        author = ctx['author'] = users.getUser(req.authname)

        if req.authname == 'anonymous':
            conf.redirect(req)

        # TODO: are recent_public and active_public lists really needed?
        actions = {"new":self.new_project_form,
                   "create":self.create_project,
                   "remove":self.remove_project,
                   "forkables":self._list_forkable_projects,
                   "recent_public":self._list_recent_public_projects,
                   "active_public":self._list_mostactive_public_projects
                   }

        # Default action
        action = 'list'

        # Try if other action is given
        try:
            act = str(req.path_info.rsplit('/', 1)[1])

            if act in actions:
                action = act
        except:
            self.log.debug("ProjectListModule.process_request failed splitting action.")

        if action in self.project_listings and not author.isProjectBrowsingAllowed():
            req.redirect(conf.url_home_path)

        # Run requested action
        if actions.has_key(action):
            return actions[action](req)

        req.redirect(ProjectListModule.home())

    def create_project(self, req):
        """ Handler for creating project request
        """
        req.perm.require("CREATE_PROJECT")
        if req.method != 'POST':
            return self.create_failure(req, 'POST request needed when creating a new project')

        author = get_context(req)['author']

        # If agreement needed but not getting it, show failure
        if conf.project_requires_agreed_terms and not self._is_active_user(req):
            return self.create_failure(req, 'You need to approve legal text to create a project!')

        projects = Projects()

        # Read and transform some variables
        vcs_type = req.args.get('vcstype')
        parent_project = None
        if "_project_" in req.args:
            parent_project = projects.get_project(env_name = req.args.get('_project_'))
            self.__require_permissions_for_cloning(req.authname, parent_project)
            vcs_type = conf.getVersionControlType(parent_project.env_name) # TODO: expensive call, probably needed

        # Read settings
        settings = {}
        if vcs_type:
            settings['vcs_type'] = vcs_type

        identifier = req.args.get('prj_short_name')
        name = req.args.get('prj_long_name')
        public = 'prj_is_public' in req.args

        published = None
        if public:
            published = datetime.now()

        # Create project object
        project = Project(
            id = None,
            env_name = identifier,
            project_name = name,
            description = req.args.get('prj_description'),
            author_id = author.id,
            created = None, # Use default which is now()
            published = published
        )

        # Create project environment
        try:
            projects.create_project(project, settings)
        except ProjectValidationException as exc:
            self.log.warning('Project creation failed due the validation: {0}'.format(exc.value))
            return self.create_failure(req, exc.value)
        except:
            self.log.exception('Project creation failed')
            return self.create_failure(req, _("Creating project failed. Try again later."))

        if public:
            projects.add_public_project_visibility(project.id)

        # Notify listeners. The project object still exists, but database does not
        for listener in self.project_change_listeners:
            listener.project_created(project)
            if public:
                listener.project_set_public(project)

        return self.create_success(req, project)

    def _is_active_user(self, req):
        author = get_context(req)['author']

        # Try approving
        has_agreed_terms = req.args.has_key('agreeTerms') and req.args.get('agreeTerms') == 'on'
        if has_agreed_terms and (author.status == User.STATUS_INACTIVE):
            author.activate()

        # If user in active state, it's ok
        if author.status == User.STATUS_ACTIVE:
            return True
        return False

    def __require_permissions_for_cloning(self, authname, parent_project):
        """ Checks that user have permissions to clone project
        """
        permissions = CQDEPermissionPolicy()
        if not permissions.check_permission(parent_project.trac_environment_key, 'VERSION_CONTROL_VIEW', authname):
            prj_name = parent_project.project_name
            env_name = parent_project.env_name
            self.log.error("Intrusive version control clone from " + env_name + " requested by " + authname + " !")
            msg = "You need to have permissions to read repository to clone it."
            raise PermissionError('VERSION_CONTROL_VIEW', env_name + "/" + prj_name, self.env, msg)

    def create_failure(self, req, msg):
        author = get_context(req)['author']

        data = {}
        data['url'] = ProjectListModule.url
        data['home'] = req.base_path
        data['user'] = author
        data['vcslist'] = self._list_enabled_vcs()
        data['prj_is_public'] = sanitize_html(req.args.get('prj_is_public', 'off'))

        # Use system warning to notify user
        add_warning(req, msg)

        for key in req.args:
            if key in ['prj_long_name', 'prj_short_name', 'prj_description',
                       'vcstype', '_project_']:
                data[key] = sanitize_html(req.args[key])

        return 'create_form.html', data, None

    def create_success(self, req, project):
        req.redirect(conf.url_projects_path + "/" + project.env_name)

    def remove_project(self, req):
        """
        Handler for removing project

        :param Request req: Trac request

        Handler expects to have following arguments in it:

        - project: Name of the project env
        - goto: Optional URL where to go after project removal. Defaults to /home/myprojects

        """
        backurl = req.args.get('goto', ProjectListModule.home('myprojects'))
        short_name = req.args.get('project')
        if not short_name:
            return self.remove_failure(req)
        if req.args.get('cancel'):
            add_notice(req, 'Project deletion cancelled')
            return self.remove_failure(req)
        author = req.authname
        prjs = Projects()
        project = prjs.get_project(env_name = short_name)

        if project is None:
            add_warning(req, 'Specified project does not exist!')
            return self.remove_failure(req)

        # Don't allow removing home
        if project.env_name == conf.sys_home_project_name:
            add_warning(req, 'Cannot remove home project')
            return self.remove_failure(req)
        if req.method != 'POST':
            return self.remove_failure(req, project=project)

        try:
            project.validate()
        except ProjectValidationException:
            req.redirect(backurl)

        # Check the permissions and method
        if ('TRAC_ADMIN' in req.perm or prjs.is_project_owner(project.env_name, author)) and req.method == 'POST':
            archive = ProjectArchive()
            # Archive the project before removal
            if not archive.archive(project):
                add_warning(req, 'Could not archive project "%s". Will not remove the project' % project.project_name)
            elif prjs.remove_project(project):
                # Notify listeners
                for listener in self.project_change_listeners:
                    listener.project_deleted(project)
                # Notify end user
                add_notice(req, 'Project "%s" removed' % project.project_name)
            else:
                add_warning(req, 'Could not remove project "%s". Try again later' % project.project_name)
        else:
            add_warning(req, 'You are not allowed to remove project "%s" (check permissions and method)' % project.project_name)

        req.redirect(backurl)

    def remove_failure(self, req, project=None):
        backurl = req.args.get('goto')
        backurl = safe_address(self.env, backurl) or ProjectListModule.home()
        if not 'TRAC_ADMIN' in req.perm:
            req.redirect(backurl)
        data = {
            'env_name': req.args.get('project'),
            'project': project,
            'goto': backurl
        }
        return 'project_remove_form.html', data, None

    def new_project_form(self, req):
        req.perm.require("CREATE_PROJECT")
        author = get_context(req)['author']

        data = {}
        data['url'] = ProjectListModule.url
        data['vcslist'] = self._list_enabled_vcs()
        data['user'] = author
        data['prj_is_public'] = sanitize_html(req.args.get('prj_is_public'))

        return 'create_form.html', data, None

    def _list_enabled_vcs(self):
        """ This function checks from the trac configuration
        what scm systems are enabled.
        """
        # FIXME: Home environment should not have any scm systems enabled
        #        this function should simply return a list from configuration
        vcsi = {}
        vcs_list = []
        from trac.core import ComponentMeta
        for component in ComponentMeta._components:
            module = sys.modules[component.__module__].__name__
            module = module.lower()
            if self.env.is_component_enabled(component):
                if module.startswith('tracext.git.') and 'git' not in vcsi.keys():
                    vcs_list.append({ 'name': 'GIT', 'id': 'git' })
                    vcsi['git'] = 1
                elif module.startswith('tracext.hg.') and 'hg' not in vcsi.keys():
                    vcs_list.append({ 'name': 'Mercurial', 'id': 'hg' })
                    vcsi['hg'] = 1
                elif module.startswith('tracbzr.') and 'bzr' not in vcsi.keys():
                    vcs_list.append({ 'name': 'Bazaar', 'id': 'bzr' })
                    vcsi['bzr'] = 1
                elif module.startswith('tracext.perforce.') and 'pf' not in vcsi.keys():
                    vcs_list.append({ 'name': 'Perforce', 'id': 'pf' })
                    vcsi['pf'] = 1

        return vcs_list

    def _list_recent_public_projects(self, req):
        prjs = Projects()

        page_size = 25

        data = {}
        limit_start, page_size = self._add_rss_pagination(req, data, page_size)

        users = conf.getUserStore()
        anon = users.getUser('anonymous')
        if anon:
            data['projects'] = prjs.get_projects_for_rss(anon.id, limit_start, page_size, "NEWEST")

        return 'rss_list.html', data, None

    def _list_mostactive_public_projects(self, req):
        prjs = Projects()

        page_size = 25

        data = {}
        limit_start, page_size = self._add_rss_pagination(req, data, page_size)
        users = conf.getUserStore()
        anon = users.getUser('anonymous')
        if anon:
            data['projects'] = prjs.get_projects_for_rss(anon.id, limit_start, page_size, "MOSTACTIVE")

        return 'rss_list.html', data, None

    def _add_rss_pagination(self, req, data, page_size):
        prjs = Projects()

        # Read selected page
        selected_page = req.args.get('page')
        if not selected_page:
            selected_page = 1
        selected_page = int(selected_page)
        data['selected_page'] = selected_page

        count = prjs.public_project_count()

        # Create array of page numbers that will be used on view
        page_count = int(math.ceil((float(count) / page_size)))
        data['pages'] = range(1, page_count + 1)

        # Create start point for limit and get all projects
        limit_start = (selected_page - 1) * page_size

        return limit_start, page_size

    def _list_forkable_projects(self, req):
        projects = Projects()
        projects = projects.get_forkable_projects(req.authname)
        return 'project_select_box.html', {'projects':projects}, None

    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        return []
