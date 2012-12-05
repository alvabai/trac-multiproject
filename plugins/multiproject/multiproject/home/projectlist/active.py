# -*- coding: utf-8 -*-
"""
Contains the UI elements for retrieving and showing active projects
"""
from pkg_resources import resource_filename

from trac.config import IntOption
from trac.core import Component, implements
from trac.web.chrome import ITemplateProvider, Chrome
from trac.wiki.api import IWikiMacroProvider, parse_args

from multiproject.common.projects import Projects
from multiproject.core.users import get_userstore


class ActiveProjectsComponent(Component):
    implements(IWikiMacroProvider, ITemplateProvider)

    min_activity = IntOption('multiproject-projects', 'min_activity',
        default=0, doc='Minimum activity expected from projects to be listed. Zero (default) means no expectations')

    # Macros
    macros = {
        'ActiveProjects': '''
Provides a block for listing the most active projects

Example usage:
{{{
[[ActiveProjects]]
[[ActiveProjects(count=5]]
}}}
''',
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
        Supported arguments:

        - count: Number of entries to show

        """
        req = formatter.req
        papi = Projects()
        userstore = get_userstore()
        projects = []

        # Parse optional arguments
        if args is None:
            args = parse_args(content)
            if len(args) > 1:
                args = args[1]

        projects = papi.get_projects_for_rss('MOSTACTIVE', limit_count=args.get('count', 5), limit_activity=self.min_activity)

        return Chrome(self.env).render_template(req, 'multiproject_active.html', {'active_projects': projects}, fragment=True)

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        """
        Return a list of directories with static resources (such as style
        sheets, images, etc.)
        """
        return []

    def get_templates_dirs(self):
        return [resource_filename('multiproject.home.projectlist', 'templates')]


