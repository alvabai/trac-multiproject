# -*- coding: utf-8 -*-
from trac.web.href import Href
from trac.mimeview.api import Context
from trac.env import open_environment
from trac.resource import Resource

from multiproject.core.configuration import conf
from multiproject.core.stubs.RequestStub import DummyReq
from multiproject.core.permissions import CQDEPermissionPolicy
from multiproject.project.timeline import ProjectTimelineEvents

class WatchlistEvents(object):
    """
    WatchlistEvents is a helper class for requesting the events based on
    given project and time range (since until current timestamp)

    """

    def get_project_events(self, project, days, minutes):
        """ List all events in project that happened in a given time span.
        """
        events = []
        project_href = Href(conf.url_projects_path + "/" + project.env_name)

        req = DummyReq('user', 'password', 'method', 'uri', 'args')
        req.permissions = (
        'TICKET_VIEW', 'CHANGESET_VIEW', 'WIKI_VIEW', 'ATTACHMENT_VIEW', 'DISCUSSION_VIEW', 'MILESTONE_VIEW')
        req.authname = 'authname'
        req.abs_href = project_href

        project_env = open_environment(conf.getEnvironmentSysPath(project.env_name), use_cache=True)
        event_provider = ProjectTimelineEvents(project_env)
        last_events = event_provider.get_timeline_events(req,
            time_in_days=days,
            time_in_minutes=minutes)

        for event in last_events:
            context = Context(resource=Resource(), href=project_href)
            context.req = req
            context.perm = req.perm
            events.append([project, event, context])

        events.sort(lambda x, y: cmp(y[1]['date'], x[1]['date']))
        return events

    def filter_events(self, events, user, project):
        """ Filter event list based on user's permissions
        """
        filtered_events = []
        policy = CQDEPermissionPolicy()
        permission_map = {
            'newticket': 'TICKET_VIEW',
            'closedticket': 'TICKET_VIEW',
            'reopenedticket': 'TICKET_VIEW',
            'changeset': 'CHANGESET_VIEW',
            'wiki': 'WIKI_VIEW',
            'attachment': 'ATTACHMENT_VIEW',
            'newmessage': 'DISCUSSION_VIEW',
            'newtopic': 'DISCUSSION_VIEW',
            'newforum': 'DISCUSSION_VIEW',
            'milestone': 'MILESTONE_VIEW'
        }

        for event in events:
            event_type = event[1]['kind']
            perm = permission_map.get(event_type)
            if perm and policy.check_permission(project.trac_environment_key, perm, user.username):
                filtered_events.append(event)

        return filtered_events
