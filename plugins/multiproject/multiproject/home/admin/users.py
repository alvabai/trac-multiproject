# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from urllib import urlencode
from trac.admin.api import IAdminPanelProvider
from trac.core import Component, implements, TracError
from trac.perm import PermissionError, PermissionCache
from trac.resource import Resource
from trac.web.chrome import add_warning, add_script, add_stylesheet, add_notice, _, tag

from multiproject.core.permissions import CQDEOrganizationStore, CQDEUserGroupStore
from multiproject.common.notifications.email import EmailNotifier
from multiproject.common.projects.projects import Projects
from multiproject.common.users import OrganizationManager
from multiproject.core.users import get_userstore, DATEFORMATS
from multiproject.common.projects import projects


class UsersAdminPanel(Component):
    """ AdminPanel component for editing users
    """
    implements(IAdminPanelProvider)

    def get_admin_panels(self, req):
        """ Introduce new component into admin panel navi
        """
        if 'USER_AUTHOR' in req.perm:
            yield ('users', 'Users', 'manage', 'Manage users')

    def render_admin_panel(self, req, cat, page, path_info):
        """
        Renders admin panel and handles user edit request
        """
        # NOTE: Permissions are checked in each action separately

        # Selected user to edit
        username = req.args.get('username')
        if username:
            if req.args.get('remove'):
                return self.remove_user(req)
            return self.edit_user(req)

        # Show user listing
        return self.list_users(req)

    def list_users(self, req):
        """
        Handle user listing
        """
        req.perm.require('USER_AUTHOR')

        data = {}
        userstore = get_userstore()

        # State
        data['states'] = userstore.USER_STATUS_LABELS

        # Available backend organizations
        # TODO: Add support for listing users based on organization in user REST API
        orgman = self.env[OrganizationManager]
        data['organizations'] = [org for org in orgman.get_organizations() if org['type'] == 'backend']

        # Add jquery ui for autocomplete
        add_script(req, 'multiproject/js/jquery-ui.js')
        add_script(req, 'multiproject/js/transparency.js')
        add_script(req, 'multiproject/js/multiproject.js')
        add_script(req, 'multiproject/js/admin_user_list.js')
        add_stylesheet(req, 'multiproject/css/jquery-ui.css')

        return 'admin_user_list.html', data

    def edit_user(self, req):
        """
        Handle user edit: view & save
        """
        changes = {}

        username = req.args.get('username')
        if not username:
            add_warning(req, _('Invalid username'))
            return self.list_users(req)

        # Load user being edited
        userstore = get_userstore()
        user = userstore.getUser(username)
        if not user:
            add_warning(req, _('Invalid username (or connection error)'))
            return self.list_users(req)

        # Load user who's doing the edit
        changed_by = userstore.getUser(req.authname)
        papi = Projects()

        # Check permissions and redirect to user listing (handy after editing the user)
        req.perm.require('USER_AUTHOR', Resource('user', id=user.id))

        data = req.args
        data['user'] = user
        data['author'] = userstore.getUserWhereId(user.author_id) if user.author_id else None
        data['deputies'] = userstore.get_deputies(user.id)
        data['base_path'] = req.base_path
        data['dateformats'] = DATEFORMATS
        data['is_local'] = userstore.is_local(user)
        data['now'] = datetime.utcnow()
        data['expired'] = user.expires and ((user.expires - datetime.utcnow()).days < 0)
        data['states'] = userstore.USER_STATUS_LABELS
        data['projects'] = papi.get_authored_projects(user)

        # Add javascript libraries for datepicker and autocomplete
        add_script(req, 'multiproject/js/jquery-ui.js')
        add_stylesheet(req, 'multiproject/css/jquery-ui.css')
        add_script(req, 'multiproject/js/multiproject.js')
        add_script(req, 'multiproject/js/admin_user_edit.js')

        # If get request show edit
        if req.method.upper() == 'GET':
            return 'admin_user_edit.html', data

        # Close pressed: get back to user listing
        if req.args.get('close'):
            return req.redirect(req.href('admin/users/manage'))

        if req.args.get('deputy_name'):
            if(userstore.add_deputy(user.id, req.args.get('deputy_name'))):
                add_notice(req, _("Deputy "+req.args.get('deputy_name')+" added."))
                return_url = 'home/admin/users/manage?username='+user.username
                return req.redirect(return_url)
            else:
                add_warning(req, _("Could not add deputy. Please try again later"))

        # Handle save
        if 'limitexceeded' in req.args:
            add_warning(req, _('Picture you tried to upload was too big. Try a smaller one'))

        # Update author if changed
        author_id = req.args.get('author_id', None)

        # If id field is empty but name is not: manual input
        if not author_id and req.args.get('author_text'):
            add_warning(req, _('Author cannot be found'))
            return 'admin_user_edit.html', data

        # Check set reset the author
        if author_id:
            author = userstore.getUserWhereId(int(author_id))
            if not author:
                add_warning(req, _('Author cannot be found'))
                return 'admin_user_edit.html', data

            # Check if author is valid: has permission to author?
            perm = PermissionCache(self.env, author.username)
            if 'USER_AUTHOR' not in perm:
                add_warning(req, _('User %s cannot work as an author (does not have USER_AUTHOR permissions)' % author))
                return self.back(req)

            user.author_id = author.id
            changes['author'] = author
        else:
            user.author_id = None

        user.lastName = req.args.get('last')
        if not user.lastName:
            add_warning(req, _('Last name required'))
            return self.back(req)

        old_mail = user.mail
        user.mail = req.args.get('email')
        if not user.mail:
            add_warning(req, _('Email address required'))
            return self.back(req)

        if old_mail != user.mail:
            changes['email'] = user.mail
            org_store = CQDEOrganizationStore.instance()
            # TODO: is this correct?
            # When changing email, reset organizations to which the user belongs in
            user.organization_keys = org_store.get_organization_keys(user) or None

        # Update password if changed
        password = req.args.get('password')
        if password:
            if not userstore.is_local(user):
                add_warning(req, _("Can't change password for user that uses external authentication method"))
                return self.back(req)

            if len(password) < 7:
                add_warning(req, _("Password must be at least 7 characters long - please provide longer password"))
                return self.back(req)

            if password != req.args.get('confirmpw'):
                add_warning(req, _("Password do not match - please check"))
                return self.back(req)

        user.givenName = req.args.get('first')
        user.mobile = req.args.get('mobile')

        # Set or reset account expiration date
        expiration_str = req.args.get('expires', '')
        if expiration_str:
            try:
                # Parse date and set expiration time in the end of the day
                expires = datetime.strptime(expiration_str, DATEFORMATS['py'])
                expires += timedelta(hours=23, minutes=59, seconds=59)

                # If changed
                if expires != user.expires:
                    user.expires = expires
                    changes['expiration_date'] = user.expires.strftime(DATEFORMATS['py'])

            except Exception:
                self.log.exception('Date formatting failed')
                add_warning(req, _('Non-recognized expiration format'))
                pass

        # Remove expiration date
        elif user.expires:
            changes['expiration_date'] = 'Never expires'
            user.expires = None

        # Update status if set
        status = int(req.args.get('status', 0))
        if status and status in userstore.USER_STATUS_LABELS.keys() and user.status != status:
            changes['status'] = userstore.USER_STATUS_LABELS[status]
            user.status = status

        if req.args.get('removeicon'):
            user.icon = None
        else:
            icon = req.args.get('icon')
            if not isinstance(icon, unicode) and icon.filename:
                user.createIcon(req.args.get('icon'))

        self.log.info('Saving changes to user: %s' % user)
        ok = userstore.updateUser(user)
        if ok and password:
            changes['password'] = password
            ok = userstore.updatePassword(user, password)

        if not ok:
            add_warning(req, _("Could not save changes"))

        add_notice(req, _("User %s updated" % username))

        # Notify user about changes via email?
        if req.args.get('notify'):
            data = {
                'user':user,
                'changed_by':changed_by,
                'changes':changes
            }

            try:
                enotify = EmailNotifier(self.env, "Account updated", data)
                enotify.template_name = 'account_edited.txt'
                enotify.notify(user.mail)
                add_notice(req, _("Notified user about the changes"))
            except TracError:
                add_warning(req, _("Failed to send email notification - user changed anyway"))

        # Check if user has still (after modification) permission to modify user
        # NOTE: req.perm cannot be used here because it is not updated yet
        resource = Resource('user', id=user.id)
        perm = PermissionCache(self.env, username=req.authname)
        if perm.has_permission('USER_AUTHOR', resource):
            return self.back(req)

        add_notice(req, _('You have no longer permission to modify the account: %s' % user.username))
        return req.redirect(req.href('admin/users/manage'))

    def remove_user(self, req):
        """
        Show removal form and handle POST as remove action
        """
        username = req.args.get('username')

        # Check method and permissions
        if not req.method.upper() == 'POST' or not username:
            raise PermissionError()

        # Load user
        userstore = get_userstore()
        user = userstore.getUser(req.authname)
        account = userstore.getUser(username)

        if not account:
            add_warning(req, "Could not find user '{0}' from service".format(account.username))
            return req.redirect(req.href('admin/users/manage'))

        # Check permissions
        req.perm.require('USER_AUTHOR', Resource('user', id=account.id))

        # If removable user is project author, change the ownership to person who deletes the user
        papi = projects.Projects()
        for project in papi.get_authored_projects(account):
            project.author = user
            project.save()

            # Check if user has TRAC_ADMIN rights for the new project, if not, try setting
            if not req.perm.has_permission('TRAC_ADMIN', Resource('project', id=project.id)):
                groupstore = CQDEUserGroupStore(project.trac_environment_key)
                # Iterate existing project groups and put user into group with TRAC_ADMIN rights
                for gname, pname in groupstore.get_all_group_permissions():
                    if pname == 'TRAC_ADMIN':
                        groupstore.add_user_to_group(project.author.username, gname)
                        self.log.info('Added TRAC_ADMIN permissions to {0} at {0}'.format(project.author, project))

            self.log.info('Changed ownership of project {0} from {0} to {0}'.format(project, project.author, user))
            add_notice(req, tag(_("Changed ownership of the project to you: "), tag.a(project.project_name, href=req.href('..', project.env_name))))

        if userstore.deleteUser(account):
            add_notice(req, "Removed user '{0}' successfully from local store".format(account.username))
        else:
            add_warning(req, "Failed to remove user '{0}' from local store".format(account.username))

        # Redirect to user listing
        return req.redirect(req.href('admin/users/manage'))


    def back(self, req):
        """
        Returns redirect request back to requested URL

        :param Request req: Request
        :returns: Request
        """
        # NOTE: Isn't there really a similar method/form validation support in Trac?
        return req.redirect(req.environ['REQUEST_URI'])
