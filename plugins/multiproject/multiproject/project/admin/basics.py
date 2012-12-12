# -*- coding: utf-8 -*-
import os
from hashlib import md5

import Image, ImageFile
from trac.core import implements
from trac.config import Option
from trac.perm import PermissionCache
from trac.web import IRequestFilter
from trac.web.chrome import Chrome, add_notice, add_warning, add_script, add_stylesheet, tag
from trac.util.translation import _
from trac.core import TracError, ExtensionPoint
from trac.admin.web_ui import BasicsAdminPanel
from trac.admin.api import IAdminPanelProvider

from multiproject.common.projects import Project
from multiproject.common.projects import Projects
from multiproject.common.projects.commands import MakeProjectPublic
from multiproject.common.projects.listeners import IProjectChangeListener
from multiproject.core.permissions import CQDEUserGroupStore
from multiproject.core.configuration import conf, DimensionOption
from multiproject.core.users import get_userstore


class BasicsAdminPanelInterceptor(BasicsAdminPanel):
    """
    Component for extending existing BasicsAdminPanel so that database
    projects table will be refreshed when user changes basic project
    information
    """
    implements(IRequestFilter, IAdminPanelProvider)

    # Extension points
    project_change_listeners = ExtensionPoint(IProjectChangeListener)
    icon_dir = Option('multiproject-projects', 'icon_dir', default='', doc='Directory where to place project icon')
    icon_size = DimensionOption('multiproject-projects', 'icon_size', default='64x64', doc='Icon size, separated with comma or x. Example: 64x64')
    content_types = {
        'image/png': 'png',
        'image/jpeg': 'jpeg',
        'image/jpg': 'jpeg',
    }

    # IRequestFilter methods

    def pre_process_request(self, req, handler):
        """
        Process request to add some data in request
        """
        return handler

    def post_process_request(self, req, template, data, content_type):
        """
        Provide ``icon_size`` config option available on all templates
        """
        if data:
            data.update({
                'icon_size': self.icon_size
            })

        return template, data, content_type

    # IAdminPanelProvider methods

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

            # Set public pressed
            if 'makepublic' in req.args:
                if conf.allow_public_projects:
                    self._make_public(req, project)
                    papi.add_public_project_visibility(project.id)
                else:
                    raise TracError("Public projects are disabled", "Error!")

            # Set private pressed
            if 'makeprivate' in req.args:
                self._make_private(req, project)
                papi.remove_public_project_visibility(project.id)

            # Remove icon if requested
            if 'reset' in req.args:
                project.icon_name = None

            # Update icon if set
            if not isinstance(req.args.get('icon', ''), basestring):
                icon_name = self._set_icon(req, project)
                if icon_name:
                    project.icon_name = icon_name
                else:
                    add_warning(req, 'Failed to set the project icon')

            # Save changes
            if 'apply' in req.args:
                self._apply_changes(req, project)

            # Reload page
            return req.redirect(req.href(req.path_info))

        data = {
            'user': user,
            'icon_size': self.icon_size,
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
                tag.a(_('public groups added'), href=req.href('admin/permissions/groupspermissions'))
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
                tag.a(_('public groups removed'), href=req.href('admin/permissions/groupspermissions'))
            ))
        else:
            add_warning(req, "Failed to unpublish project")

    def _set_icon(self, req, project):
        """
        Stores the icon set in request into filesystem with format: <pid>-<contentmd5>.<format>
        """
        icon = req.args.get('icon')

        icon_data = icon.value
        icon_format = icon.type
        icon_size = self.icon_size

        hash = md5()
        hash.update(icon_data)
        icon_name = '%d-%s.%s' % (project.id, hash.hexdigest(), self.content_types[icon_format])
        icon_path = os.path.join(self.icon_dir, icon_name) if self.icon_dir else os.path.join(self.env.path, 'htdocs', icon_name)
        icon_width, icon_height = icon_size['width'], icon_size['height']

        # Resize and save the image
        with open(icon_path, 'w+b') as fd:
            p = ImageFile.Parser()
            p.feed(icon_data)
            img = p.close()

            try:
                # Resize first by keeping the ratio, then convert to have alpha channel and then for to given size
                img.thumbnail((icon_width, icon_height), Image.ANTIALIAS)
                img = img.convert("RGBA")
                img = img.transform((icon_width, icon_height), Image.EXTENT, (0, 0, icon_width, icon_height))
                img.save(icon_path)
                self.log.info('Saved project icon to %s' % icon_path)
            except IOError, err:
                self.log.error('Failed to save project icon: %s' % icon_path)
                return None

        return icon_name


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
                        permlink = tag.a('You way want to modify permissions', href=req.href('admin/permissions/groups'))
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

