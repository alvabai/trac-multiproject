# -*- coding: utf-8 -*-
"""
Contains the UI elements for featured projects
"""
from pkg_resources import resource_filename

from trac.core import Component, implements
from trac.web.chrome import ITemplateProvider, Chrome
from trac.wiki.api import IWikiMacroProvider, parse_args

from multiproject.common.projects import Projects
from multiproject.core.users import get_userstore


class FeaturedProjectsComponent(Component):
    implements(IWikiMacroProvider, ITemplateProvider)

    # Macros
    macros = {
        'FeaturedProjects': '''
Provides a block for listing latest featured projects

Example usage:
{{{
[[FeaturedProjects]]
[[FeaturedProjects(count=5]]
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

        # Parse optional arguments
        if args is None:
            args = parse_args(content)
            if len(args) > 1:
                args = args[1]

        featured_projects = papi.get_projects_for_rss('FEATURED', limit_count=args.get('count', 5))

        data = {
            'featured_projects': featured_projects
        }
        return Chrome(self.env).render_template(req, 'multiproject_featured.html', data, fragment=True)

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        """
        Return a list of directories with static resources (such as style
        sheets, images, etc.)
        """
        return []

    def get_templates_dirs(self):
        return [resource_filename('multiproject.common.featured', 'templates')]
