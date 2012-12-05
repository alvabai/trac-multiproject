# -*- coding: utf-8 -*-
from trac.perm import PermissionCache
from trac.web.chrome import Chrome, add_notice, add_warning, add_script, add_stylesheet, tag
from trac.util.translation import _
from trac.core import TracError, ExtensionPoint
from trac.admin.web_ui import BasicsAdminPanel

from multiproject.common.projects import Project
from multiproject.common.projects import Projects
from multiproject.common.projects.commands import MakeProjectPublic
from multiproject.common.projects.listeners import IProjectChangeListener
from multiproject.core.permissions import CQDEUserGroupStore
from multiproject.core.configuration import conf
from multiproject.core.users import get_userstore


class BasicsAdminPanelInterceptor(BasicsAdminPanel):
    """
    Component for extending existing BasicsAdminPanel so that database
    projects table will be refreshed when user changes basic project
    information
    """
    # Extension points
    project_change_listeners = ExtensionPoint(IProjectChangeListener)

    def render_admin_panel(self, req, cat, page, path_info):
        """ Overrides BasicsAdminPanel rendering function.

            Handle project info update (update global db) and then
            delegate handling back to BasicsAdminPanel
        """
        req.perm.require('TRAC_ADMIN')
        userstore = get_userstore()
        user = userstore.getUser(req.authname)

        project = Project.get(self.env)

        # Update database if form posted
        if req.method == 'POST':
            papi = Projects()
            if req.args.has_key('makepublic'):
                if conf.allow_public_projects:
                    self._make_public(req, project)
                    papi.add_public_project_visibility(project.id)
                else:
                    raise TracError("Public projects are disabled", "Error!")

            if req.args.has_key('makeprivate'):
                self._make_private(req, project)
                papi.remove_public_project_visibility(project.id)

            if req.args.has_key('apply'):
                self._apply_changes(req, project)

            # Reload page
            return req.redirect(req.href(req.path_info))

        data = {
            'user': user,
            'mproject': project,
            'is_public': project.public,
            'allow_public_projects': conf.allow_public_projects
        }

        # Add javascript libraries for datepicker and autocomplete
        add_script(req, 'multiproject/js/jquery-ui.js')
        add_stylesheet(req, 'multiproject/css/jquery-ui.css')
        add_script(req, 'multiproject/js/multiproject.js')
        add_script(req, 'multiproject/js/admin_basics.js')

        Chrome(self.env).add_textarea_grips(req)
        return 'admin_basics_replacement.html', data

    def _make_public(self, req, project):
        cmd = MakeProjectPublic(project)
        if cmd.do():
            # Notify listeners
            for listener in self.project_change_listeners:
                listener.project_set_public(project)
            # Notify user
            add_notice(req, tag(
                _("Project published: "),
                tag.a(_('public groups added'), href=req.href('admin/general/permissions'))
            ))
        else:
            add_warning(req, "Failed to publish project")

    def _make_private(self, req, project):
        cmd = MakeProjectPublic(project)
        if cmd.undo():
            # Notify listeners
            for listener in self.project_change_listeners:
                listener.project_set_private(project)
            # Notify user
            add_notice(req, tag(
                _("Unpublished project: "),
                tag.a(_('public groups removed'), href=req.href('admin/general/permissions'))
            ))
        else:
            add_warning(req, "Failed to unpublish project")

    def _apply_changes(self, req, project):
        """
        Saves changes into database and project configuration file
        """
        try:
            # Save information into database
            project.project_name = req.args.get('name')
            project.description = req.args.get('descr')

            # Update author if needed
            author_id = req.args.get('author_id')
            if author_id and project.author_id != int(author_id):
                userstore = get_userstore()
                author = userstore.getUserWhereId(author_id)
                project.author = author

                # Check if author has admin permission to project: put in project if not
                authorperm = PermissionCache(self.env, author.username)
                if 'TRAC_ADMIN' not in authorperm:
                    admin_rights = False
                    groupstore = CQDEUserGroupStore(project.trac_environment_key)
                    # Iterate existing project groups and put user into group with TRAC_ADMIN rights
                    for gname, pname in groupstore.get_all_group_permissions():
                        if pname == 'TRAC_ADMIN':
                            groupstore.add_user_to_group(author.username, gname)
                            admin_rights = True
                            add_notice(req, _('Added TRAC_ADMIN permissions to user: {0}'.format(author.username)))

                    if not admin_rights:
                        permlink = tag.a('You way want to modify permissions', href=req.href('admin/general/permissions'))
                        add_warning(req, tag(_('User {0} does not have administrative rights to project. '.format(author.username)), permlink))

            # Save changes to database
            project.save()

            # Save information into config
            for option in ('name', 'descr'):
                self.config.set('project', option, req.args.get(option))
            self.config.save()

        except Exception, e:
            self.log.exception('Failed to save project changes')
            add_warning(req, _('Failed to save changes: {0}'.format(e)))
            return req.redirect(req.href('admin/general/basics'))

        add_notice(req, _('Project changes saved'))

