# -*- coding: utf-8 -*-
"""
Module provides the request handler and wiki macro for project watching/following.

Macros:
    - ``[[WatchProject]]``: Create a info box about project following, showing the status and follow buttons.

REST API:
    - Start following: ``/api/project/<pid>/watch?action=watch``
    - Stop following: ``/api/project/<pid>/watch?action=unwatch``
    - Show status: ``/api/project/<pid>/watch``

      Example output:

        {"is_watching": false, "project_id": 71, "count": 234}

"""
import re

from pkg_resources import resource_filename
from trac.core import Component, implements
from trac.wiki.api import parse_args
from trac.web.api import IRequestHandler
from trac.wiki.api import IWikiMacroProvider
from trac.web.chrome import add_script, ITemplateProvider, Chrome, tag, _

from multiproject.core.restful import send_json
from multiproject.core.users import get_userstore
from multiproject.core.watchlist import CQDEWatchlistStore
from multiproject.common.projects.projects import Projects


REQ_REGEXP = re.compile('\/api\/project/(?P<pid>\d+)\/watch')


class WatchProjectsModule(Component):
    implements(IRequestHandler, IWikiMacroProvider, ITemplateProvider)

    # Macros
    macros = {
        'WatchProject': '''
Provides a block for following the project: show status and
provide buttons for following/unfollowing. Optional arguments:

- project: Name of the project environment. Defaults to current project

Example usage:
{{{
[[WatchProject]]
[[WatchProject(project=projectx]]
}}}
''',
    }

    # IRequestHandler methods

    def match_request(self, req):
        """
        Match /watch path to this page
        """
        return REQ_REGEXP.match(req.path_info)

    def process_request(self, req):
        req.perm.require('TIMELINE_VIEW')

        userstore = get_userstore()
        watchstore = CQDEWatchlistStore()
        action = req.args.get('action')
        project_id = 0

        # Determine project id from URL
        match = REQ_REGEXP.match(req.path_info)
        if match:
            project_id = int(match.group('pid'))

        # Load userinfo
        user = userstore.getUser(req.authname)
        uid = user.id if user else None

        is_watching = watchstore.is_watching(uid, project_id)
        watchers = len(watchstore.get_watchers_by_project(project_id))

        # Return status
        if not action or not uid or req.authname == 'anonymous':
            data = {
                'project_id': project_id,
                'is_watching': is_watching,
                'count' : watchers
            }
            return send_json(req, data)

        # Start following
        elif action == 'watch':
            watchstore.watch_project(uid, project_id)

        # Stop following
        elif action == 'unwatch':
            watchstore.unwatch_project(uid, project_id)

        return send_json(req, 'ok')

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

        - project: Name of the project to show status / provide follow buttons. Defaults to current project

        """
        req = formatter.req

        # Parse optional arguments
        if args is None:
            args = parse_args(content)
            if len(args) > 1:
                args = args[1]

        # Read optional project name - fallback to current
        project_name = self.env.path.rsplit('/', 1)[1]
        if args and 'project' in args:
            project_name = args.get('project', '').strip()

        # Load project id from db
        papi = Projects()
        project_id = papi.get_project_id(project_name)

        # Show macro only when user has permission to view timeline
        if name not in self.macros or 'TIMELINE_VIEW' not in req.perm or not project_id:
            # Return default content / instructions
            return tag.div(
                tag.h2(_('Follow project'), **{'class': 'title'}),
                tag.p(_('Project cannot be found or no permission to follow it')),
                **{'class': 'watch'}
            )

        # For anonymous users, advice login/registering
        if req.authname == 'anonymous':
            return tag.div(
                tag.h2(_('Follow project'), **{'class': 'title'}),
                tag.p(_('Only registered users can follow the project activity. ')),
                tag.p(tag.a('Please login or register to service first', href=req.href('../home/user'))),
                **{'class': 'watch'}
            )

        # Return rendered HTML with JS attached to it
        data = {
            'project_id': project_id,
            'env_name': self.env.path.rsplit('/', 1)[1],
            'project_name': project_name
        }

        # FIXME: Script does not get loaded in all setups. Using script element in template instead
        #add_script(req, 'multiproject/js/watch.js')
        return Chrome(self.env).render_template(req, 'multiproject_watch.html', data, fragment=True)

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        """
        Return a list of directories with static resources (such as style
        sheets, images, etc.)
        """
        return [('multiproject', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return []

