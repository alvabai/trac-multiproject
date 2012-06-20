# -*- coding: utf-8 -*-
"""
Provides components for project team listing and handling.
"""
from pkg_resources import resource_filename
from trac.wiki.api import IWikiMacroProvider
from trac.core import Component, implements
from trac.web.chrome import ITemplateProvider, tag, Markup, _, Chrome

from multiproject.common.projects.projects import Projects
from multiproject.core.configuration import conf
from multiproject.core.permissions import CQDEUserGroupStore
from multiproject.core.users import get_userstore


class ProjectTeam(Component):
    implements(IWikiMacroProvider, ITemplateProvider)

    # Macros
    macros = {
        'ProjectTeam': 'Show team contents in a block'
    }

    # IWikiMacroProvider methods

    def get_macros(self):
        for macro in self.macros:
            yield macro

    def get_macro_description(self, name):
        return self.macros.get(name)

    def expand_macro(self, formatter, name, content, args=None):
        """
        Returns the outcome from macro.
        """
        req = formatter.context.req

        # Check permissions
        if 'TIMELINE_VIEW' not in req.perm:
            # Return default content / instructions
            return tag.div(
                tag.h2(_('Project team'), **{'class': 'title'}),
                tag.p(_('Project team cannot be found or no permission to follow it')),
                **{'class': 'watch'}
            )

        # Load project info from optional project argument. Defaults to current env
        project_name = self.env.path.rsplit('/', 1)[1]

        papi = Projects()
        project = papi.get_project(env_name=project_name)
        team, members = self._get_team_info(project)

        # Return rendered HTML with JS attached to it
        data = {
            'project_id': project.id,
            'env_name': self.env.path.rsplit('/', 1)[1],
            'project_name': project_name,
            'team': team,
        }

        return Chrome(self.env).render_template(req, 'multiproject_team.html', data, fragment=True)

    # Internal methods

    def _get_team_info(self, project):
        """
        Reads team members and sorts them so that default groups
        are first and other groups are last (in alphabetical order)

        :param Project project: Project to retrieve team info from
        :returns: tuple of data: teams, members
        """
        ug = CQDEUserGroupStore(project.trac_environment_key)
        team = sorted(ug.get_all_user_groups(), key = lambda tmp: tmp[1])

         # TODO: Implement better

        default_group_names = [tuple[0] for tuple in conf.default_groups]
        default_group_names += [conf.public_auth_group[0], conf.public_anon_group[0]]
        first = {}
        last = {}
        all_members = {}

        # Create group => member hash
        userstore = get_userstore()
        for member, group in team:
            all_members[member] = 1
            account = userstore.getUser(username=member)

            if group in default_group_names:
                if group not in first:
                    first[group] = []
                first[group].append(account)
            else:
                if group not in last:
                    last[group] = []
                last[group].append(account)

        # Create group, memberlist tuples from items and keep them sorted
        # First read the default groups in to list of tuples in the order they are defined in conf
        items = []
        for group in default_group_names:
            if first.has_key(group):
                items += [(group, first[group])]

        # Then append other groups in alphabetical order
        items += sorted(last.items(), key = lambda tmp: tmp[0])

        # Then join all the members as a one markup string with member links
        teams = []
        for group, members in items:
            teams.append((group, members))

        # Team members in (group, member_uri) type, and all member names
        return teams, all_members.keys()

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        """
        Return a list of directories with static resources (such as style
        sheets, images, etc.)
        """
        return [('multiproject', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return []