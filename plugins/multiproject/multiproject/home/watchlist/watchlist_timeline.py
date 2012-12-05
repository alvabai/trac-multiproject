# -*- coding: utf-8 -*-
import re
from pkg_resources import resource_filename

from trac.core import Component, implements
from trac.web import IRequestHandler
from trac.web.chrome import ITemplateProvider

from multiproject.common.projects import Project
from multiproject.core.configuration import conf
from multiproject.core.users import get_userstore
from multiproject.core.util import to_web_time
from multiproject.core.watchlist import CQDEWatchlistStore
from multiproject.home.watchlist.watchlist_events import WatchlistEvents


class WatchlistTimeline(Component):
    """
    This trac component shows full timeline for the projects followed/watched by the user.
    View can be seen at path::

            home/watchlist_timeline

    .. NOTE::

       Plugin should be enabled only for home project.
    """
    implements(ITemplateProvider, IRequestHandler)

    # IRequestHandler methods
    def match_request(self, req):
        """ Match /welcome path to this page
        """
        return re.match(r'/watchlist_timeline(?:_trac)?(?:/.*)?$', req.path_info)

    def process_request(self, req):
        """ Render page
        """
        if req.authname == 'anonymous':
            conf.redirect(req, conf.url_home_path + '/user')

        # Prepare data for template
        data = {}
        data['baseurl'] = conf.url_projects_path
        data['base_path'] = req.base_path
        data['watchlist'] = self._get_watchlist_events(req)
        data['to_web_time'] = to_web_time

        if req.args.get('format') == 'rss':
            return "watchlist_timeline.rss", data, 'application/rss+xml'

        return "watchlist_timeline.html", data, None

    # ITemplateProvider methods
    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        return []

    def _get_watchlist_events(self, req):
        events = []
        user = get_userstore().getUser(req.authname)
        if not user:
            return None

        watchlist = CQDEWatchlistStore().get_projects_by_user(user.id)
        event_helper = WatchlistEvents(self.env)
        # TODO: inefficient querying
        for watch in watchlist:
            project = Project.get(id=watch.project_id)
            project_events = event_helper.get_project_events(project, days = 7, minutes = 0)
            # filter eventlist by user's permissions
            project_events = event_helper.filter_events(project_events, user, project)
            if project_events:
                events.extend(project_events)

        events.sort(lambda x, y: cmp(y[1]['date'], x[1]['date']))
        return events

