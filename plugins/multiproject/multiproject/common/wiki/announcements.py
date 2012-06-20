# -*- coding: utf-8 -*-
"""
News forum macro for wiki pages, to list project news, or some other project news.

This can be embedded on any wiki page instead of it being hard coded into the
Project Summary page.
"""
from pkg_resources import resource_filename

from trac.wiki.api import IWikiMacroProvider, parse_args
from trac.core import Component, implements, TracError
from trac.web.chrome import ITemplateProvider, Chrome

from multiproject.core.db import safe_string, safe_int
from multiproject.core.permissions import CQDEPermissionPolicy
from multiproject.core.util import to_web_time
from multiproject.project.summary.news import ProjectNews
from multiproject.common.environment import TracEnvironment


class Announcements(Component):
    """
    Render X amount of latest events from announcements board.
    """
    implements(IWikiMacroProvider, ITemplateProvider)

    # IWikiMacroProvider methods
    def get_macros(self):
        """
        Return an iterable of all macros this component provides.
        """
        return ['Announcements']

    def get_macro_description(self, name):
        """
        Return a plain text description of a macro, based on name.
        """
        if name != 'Announcements':
            return None

        return '''
Get latest news for a project, from the project's "Announcements" discussion
board. Take note that permission checks are still in place.

Arguments:

* title - Title for the section to show. Defaults to "Latest Announcements".
* count - The amount of news to list. Defaults to 5.
* project - The project to list the news from. Defaults to current project.

Example:
{{{
[[Announcements(count=10,project="multiproject")]]
}}}
Will return last 10 news from project "multiproject"
'''

    def expand_macro(self, formatter, name, content, args=None):
        """
        Expand the macro. We will accept a parameter to point us to another project
        if necessary.
        """
        if name != 'Announcements':
            return None

        data = {}

        env_name = None
        count = 0
        title = None
        env = None

        # Parse settings for the macro
        env_name, count, title = self._parse_args(args, content)

        if not count:
            self.log.debug("Defaulting count to 5")
            count = 5

        data['news_title'] = title
        current_env_name = self.env.path.split('/')[-1]

        if not env_name:
            env_name = current_env_name

        data['env_name'] = env_name

        # Check if the project exists.
        mpp_env = None
        try:
            mpp_env = TracEnvironment.read(env_name)
        except TracError:
            data['news_error'] = "Couldn't find project '{0}'".format(env_name)
            self.log.error(data['news_error'])

        # Then check the permissions
        if mpp_env:
            has_permission = CQDEPermissionPolicy().check_permission(
                mpp_env.environment_id, 'DISCUSSION_VIEW', formatter.req.authname)

            if has_permission:
                try:
                    news = ProjectNews(env_name)
                    data['newsitems'] = news.get_project_news(limit=count)
                    data['news_forum_id'] = news.get_news_forum_id()
                except Exception, e:
                    self.log.exception("Failed to read project {0} news.".format(env_name))
                    raise TracError("Couldn't read news for project '{0}': {1}".format(env_name, e))
            else:
                data['news_error'] = "No permission to read news from project '{0}'".format(env_name)

        # This function should be Genshi template macro or something
        data['to_web_time'] = to_web_time

        self.log.debug(data)

        # Render the macro content with a genshi template. Note that errors are printed on
        # screen with some user friendly texts instead of exceptions (on most common cases
        # anyway).
        return Chrome(self.env).render_template(
            formatter.req, 'announcements.html', data, 'text/html', True)

    # ITemplateProvide methods
    def get_templates_dirs(self):
        """
        Returns the directories where to ask for templates
        """
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        """
        Returns the directories (with a prefix) to get the htdocs
        """
        return []

    # "Private" methods
    def _parse_args(self, args, content):
        """
        Parse args from incoming args or from content. Depending on which is set.
        If called as a macro, the content holds the arguments. Otherwise it's
        the args param that holds the arguments.

        In macro case, a tuple is returned, first element is list of arguments,
        second is a dict. We only support the dict format.
        """
        env_name = ''
        count = 0
        title = 'Latest Announcements'

        if args is None:
            args = parse_args(content)
            if len(args) > 1:
                args = args[1]

        if args is not None and 'project' in args:
            env_name = args['project']
            env_name = env_name.strip('" \'')
            env_name = env_name.encode('utf-8')
            env_name = safe_string(env_name)

        if args is not None and 'count' in args:
            count = args['count']
            count = safe_int(count)

        if args is not None and 'title' in args:
            title = args['title']
            title = title.strip('"')

        self.log.debug("Returning args: {0}".format((env_name, count, title)))

        return env_name, count, title
