# -*- coding: utf-8 -*-
"""
Module provides the request handler and wiki macro for project watching/following.

Macros:
    - ``[[WatchProject]]``: Create a info box about project following, showing the status and follow buttons.

REST API:
    - Start following: ``/api/project/<pid>/watch?action=watch``
    - Stop following: ``/api/project/<pid>/watch?action=unwatch``

    After completing the action, page redirects to page defined with ``goto`` argument.

"""
import re

from pkg_resources import resource_filename

from genshi.filters import Transformer
from trac.core import Component, implements, TracError, ExtensionPoint
from trac.util.translation import ngettext
from trac.wiki.api import parse_args
from trac.web.api import IRequestHandler, ITemplateStreamFilter
from trac.wiki.api import IWikiMacroProvider
from trac.web.chrome import ITemplateProvider, Chrome, tag, _

from multiproject.core.users import get_userstore
from multiproject.core.watchlist import CQDEWatchlistStore
from multiproject.common.projects.projects import Project

from multiproject.common.projects.listeners import IProjectChangeListener

REQ_REGEXP = re.compile('\/api\/project/(?P<pid>\d+)\/watch')


class WatchProjectsModule(Component):
    implements(IRequestHandler, IWikiMacroProvider, ITemplateProvider, ITemplateStreamFilter)

    # Extension point
    project_change_listeners = ExtensionPoint(IProjectChangeListener)

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
        """
        Handles the request

        :param req: Request
        :return: json
        """
        if req.method != 'POST':
            raise TracError('Invalid request')

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

        #load project
        project = Project.get(id=project_id)

        # Start following
        if action == 'watch':
            watchstore.watch_project(uid, project_id)

            # Notify listeners.
            for listener in self.project_change_listeners:
                try:
                    listener.project_watchers(project)
                except:
                    pass

        # Stop following
        elif action == 'unwatch':
            watchstore.unwatch_project(uid, project_id)

        goto = req.args.get('goto', req.href(''))
        return req.redirect(goto)

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
        project_name = self.env.project_identifier
        if args and 'project' in args:
            project_name = args.get('project', '').strip()

        # Load project id from db
        project_id = Project.get(env_name=project_name).id
        watchers, is_watching = self._get_status(req, project_id)

        # If user is already watching, do not show the block
        if is_watching:
            return tag.div('')

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
            'env_name': self.env.project_identifier,
            'project_name': project_name
        }

        chrome = Chrome(self.env)
        stream = chrome.render_template(req, 'multiproject_watch.html', data, fragment=True)
        if req.form_token:
            stream |= chrome._add_form_token(req.form_token)

        return stream

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        """
        Return a list of directories with static resources (such as style
        sheets, images, etc.)
        """
        return [('multiproject', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return []

    # ITemplateStreamFilter methods

    def filter_stream(self, req, method, filename, stream, data):
        """
        Adds project follower information in project summary block::

            Followers: You and 1 other
            Followers: You and 10 others
            Followers: 10

        """
        # Filter only the summary table wiki macro
        if filename != 'multiproject_summary.html':
            return stream

        # Load project and followers info
        project = Project.get(self.env)
        watchers, is_watching = self._get_status(req, project.id)

        # By default show only the number
        status = tag.span(watchers)

        # Show link to user preferences
        if is_watching:
            status = tag.a('You', href=req.href('../home/prefs/following'))

            # And others?
            watchers -= 1
            if watchers:
                status += ngettext(" and %(count)s other", " and %(count)s others", watchers, count=watchers)

        # Add following information into project summary block
        trans = Transformer('//div[@class="summary"]/table').append(
            tag.tr(
                tag.th('Followers:'),
                tag.td(status)
            )
        )

        return stream | trans

    # Internal methods

    def _get_status(self, req, project_id):
        """
        Returns the watching status as a tuple:

        - Number of followers
        - True/False whether current user is already following or not

        :param req: Trac Request
        :return: Status
        :rtype: tuple
        """
        # Load watching info
        userstore = get_userstore()
        user = userstore.getUser(req.authname)
        watchstore = CQDEWatchlistStore()
        is_watching = False

        # NOTE: Some environments may not have special anonymous/authenticated users, thus user can be None
        if user:
            is_watching = watchstore.is_watching(user.id, project_id)
        watchers = len(watchstore.get_watchers_by_project(project_id))

        return watchers, is_watching
