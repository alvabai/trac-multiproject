# -*- coding: utf-8 -*-
"""
Module implements trac-admin commands related to home project functionality
"""
from datetime import datetime

from trac.admin.console import TracAdmin
from trac.config import Option
from trac.core import Component, implements, TracError
from trac.admin import IAdminCommandProvider, AdminCommandManager, \
    AdminCommandError, get_dir_list
from trac.util.text import print_table
from trac.env import open_environment, Environment
from trac.util.text import printout
from trac.util.translation import _

from multiproject.core.users import get_userstore
from multiproject.core.util.filesystem import safe_path
from multiproject.common.projects import Project
from multiproject.common.env import MultiProjectEnvironmentInit
from multiproject.core.db import admin_query


class HomeUserAdminCommandProvider(Component):

    implements(IAdminCommandProvider)

    # IAdminCommandProvider methods

    def get_admin_commands(self):
        yield ('mp user list expired', '<when:YYYY-MM-DD>',
               'Print list expired or soon to be expiring users. Optional date argument to check from future: YYYY-MM-DD',
               None, self._list_expired)

    def _list_expired(self, when=None):
        # Parse optional date argument
        when = when if when is None else datetime.strptime(when, '%Y-%m-%d')

        userstore = get_userstore()
        users = [(user.username, user.expires) for user in userstore.get_expired_users(when=when)]

        print_table(users, ('User', 'Expires'))

class GlobalConsoleAdmin(Component):
    implements(IAdminCommandProvider)

    # IAdminCommandProvider methods
    def get_admin_commands(self):
        yield ('mp run', '[offset:int] [limit:int] <command>',
               """Run commands in all trac environments, not including home.

                If <command> is special "upgrade-check", prints whether environment needs upgrade.

                If <command> is special "list-env", prints the same info as the 'mp list env'.
                """,
               None, self.globally_execute_command)
        yield ('mp list env', '',
               """List environments, possibly by using the given offset and limit.

                The home environment is not included.
                """,
               None, self.list_projects)
        yield ('mp ?', '<command>',
               'Get help for the command',
               None, self.globally_get_command_help)

    def list_projects(self):
        self.globally_execute_command('list-env')

    def globally_get_command_help(self, *args):
        sys_home_project_name = self.config.get('multiproject', 'sys_home_project_name')
        for env_name, in self.projects_iterator(['env_name'], batch_size=1):
            if env_name == sys_home_project_name:
                continue
            env = None

            try:
                env_path = safe_path(self.config.get('multiproject', 'sys_projects_root'),
                    env_name)
                env = open_environment(env_path, True)
            except TracError as e:
                printout(_('ERROR: Opening environment %(env_name)s failed', env_name=env_name))
                continue

            try:
                command_manager = AdminCommandManager(env)
                helps = command_manager.get_command_help(list(args))
                if not args:
                    TracAdmin.print_doc(helps, short=True)
                elif len(helps) == 1:
                    TracAdmin.print_doc(helps, long=True)
                else:
                    TracAdmin.print_doc(helps)

            except AdminCommandError as e:
                printout(_('ERROR: Getting command help in environment %(env_name)s failed: ',
                    env_name=env_name) + e)
            break

    def globally_execute_command(self, *args):
        offset = 0
        max_index = -1
        if args and args[0].isdigit():
            offset = int(args[0])
            if len(args) > 1 and args[1].isdigit():
                limit = int(args[1])
                max_index = limit + offset
                args = args[2:]
            else:
                args = args[1:]
        upgrade_check = False
        env_list = False
        if args and args[0] == 'upgrade-check':
            upgrade_check = True
        elif args and args[0] == 'list-env':
            env_list = True

        sys_home_project_name = self.config.get('multiproject', 'sys_home_project_name')
        for index, row in enumerate(self.projects_iterator(['env_name'], batch_size=10)):
            env_name, = row
            if index < offset:
                continue
            if max_index != -1 and index >= max_index:
                break
            if env_name == sys_home_project_name:
                continue
            if env_list:
                printout("{0:4} env:'{1}'".format(index, env_name))
                continue
            env = None
            try:
                env_path = safe_path(self.config.get('multiproject', 'sys_projects_root'),
                    env_name)
                env = Environment(env_path)
            except TracError as e:
                printout(_('ERROR: Opening environment %(env_name)s failed', env_name=env_name))
                continue

            if upgrade_check:
                if env.needs_upgrade():
                    printout("[+] {0:4} env:'{1}'".format(index, env_name))
                else:
                    printout("[ ] {0:4} env:'{1}'".format(index, env_name))
                continue
            # To setup MultiProject specific things like 'project_identifier'
            MultiProjectEnvironmentInit(env).environment_needs_upgrade(None)

            try:
                command_manager = AdminCommandManager(env)
                printout(_("{0:4} Run in env:'{1}'".format(index, env_name)))
                command_manager.execute_command(*args)
            except AdminCommandError as e:
                printout(_('ERROR: Executing command in environment %(env_name)s failed: ',
                    env_name=env_name) + str(e))

    def projects_iterator(self, attributes, batch_size=100):
        """
        Function yields tuples where each tuple has projects values in them,
        in the order of attributes.

        For example, if params are::

            attributes=['id', 'env_name', 'trac_environment_key']

        Returned values could be::

            [(123, 'ProjectX', 124), (124, 'ProjectY', 125)]

        """
        if not attributes:
            raise TracError(_('No attributes provided'))

        for column in attributes:
            if column not in Project.FIELDS:
                raise TracError(_('Invalid column given: "%(name)s" ', name=column))
        offset = 0
        last_count = -1
        query = """ SELECT {0} FROM projects ORDER BY project_id LIMIT %s, %s
                """.format(', '.join(["`{0}`".format(Project.FIELDS[attribute])
                                      for attribute in attributes]))
        projects = []
        while last_count:
            with admin_query() as cursor:
                try:
                    cursor.execute(query, (offset, batch_size))
                    projects = cursor.fetchall()
                    self.log.debug(query % (offset, batch_size))
                except:
                    self.log.exception("Project query failed: {0}".format(query))
                    raise
            last_count = len(projects)
            for project in projects:
                yield project
            offset += batch_size


class HomeDeployCommandProvider(Component):
    """
    This class provides a trac-admin command for deploying static htdocs
    from multiproject and other globally enabled plugins.

    .. Note::

        By default, [multiproject] static_htdocs_path configuration is used.

    """

    implements(IAdminCommandProvider)

    static_htdocs_path = Option('multiproject', 'static_htdocs_path', default='',
        doc='Path to where the static htdocs files are located.')

    # IAdminCommandProvider methods

    def get_admin_commands(self):
        yield ('mp deploy', '[path]',
               """Deploy globally static files from plugins into optional path.

                If path is not given, [multiproject] static_htdocs_path configuration is used instead.
               """,
               self._complete_deploy_command, self._do_deploy)

    def _complete_deploy_command(self, args):
        return get_dir_list(args[0])

    def _do_deploy(self, *args):
        from multiproject.core.util.statichtdocs import deploy_htdocs

        if args:
            deploy_htdocs(self.env, dest=args[0])
        else:
            deploy_htdocs(self.env)
