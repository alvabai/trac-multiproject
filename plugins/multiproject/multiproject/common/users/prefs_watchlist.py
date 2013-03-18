# -*- coding: utf-8 -*-
from trac.core import Component, implements, TracError, ExtensionPoint
from trac.prefs.api import IPreferencePanelProvider

from multiproject.common.projects import Project
from multiproject.core.users import get_userstore
from multiproject.core.watchlist import CQDEWatchlistStore
from multiproject.common.projects.listeners import IProjectChangeListener


class WatchlistPreferencePanel(Component):
    """ Preference panel for editing project watchlist
    """
    implements(IPreferencePanelProvider)

    # Extension points
    project_change_listeners = ExtensionPoint(IProjectChangeListener)
    
    def get_preference_panels(self, req):
        if req.authname != 'anonymous':
            yield ('following', 'Following')

    def render_preference_panel(self, req, panel):

        if req.authname == 'anonymous':
            raise TracError("Can't change preferences!", "No access!")

        if req.method == 'POST':
            self.save_watchlist(req)

        watchlist = []
        projects = {}
        user = get_userstore().getUser(req.authname)
        w = CQDEWatchlistStore()
        if user:
            watchlist = w.get_projects_by_user(user.id)
            # TODO: inefficient querying
            for watch in watchlist:
                projects[watch.project_id] = Project.get(id=watch.project_id)
        return 'multiproject_user_prefs_watchlist.html', { 'watchlist': watchlist, 'projects' : projects,
            'notification_values': w.notifications }

    def save_watchlist(self, req):
        user = get_userstore().getUser(req.authname)
        if not user:
            return

        w = CQDEWatchlistStore()
        if req.args.get('notification'):
            notifylist = self.__to_list(req.args.get('notification'))
            for item in notifylist:
                project_id, notification = item.split('_')
                w.watch_project(user.id, project_id, notification)
                
                # Notify listeners.
                project = Project.get(id=project_id)
                for listener in self.project_change_listeners:
                    listener.project_watchers(project)

        if req.args.get('remove'):
            removelist = self.__to_list(req.args.get('remove'))
            for project_id in removelist:
                w.unwatch_project(user.id, project_id)

    def __to_list(self, selection):
        return isinstance(selection, list) and selection or [selection]
