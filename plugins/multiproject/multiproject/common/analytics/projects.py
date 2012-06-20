# -*- coding: utf-8 -*-
"""
Module implements the project listeners for analytics, as we're interested in them.
"""
from trac.core import Component, implements

from multiproject.common.projects.listeners import IProjectChangeListener
from multiproject.core.analytics.event import EventLogIO

class ProjectAnalytics(Component):
    implements(IProjectChangeListener)

    def project_created(self, project):
        self._log_event(project, 'project_created')

    def project_set_public(self, project):
        self._log_event(project, 'project_set_public')

    def project_set_private(self, project):
        self._log_event(project, 'project_set_private')

    def project_archived(self, project):
        self._log_event(project, 'project_archived')

    def project_deleted(self, project):
        self._log_event(project, 'project_deleted')

    def _log_event(self, project, eventname):
        """
        Internal method for creating event in analytics log
        """
        self.log.info('Received notification for %s: %s' % (project, eventname))

        # Load username from project author information or fallback to anonymous
        user = project.author
        username = user.username if user else 'anonymous'

        log = EventLogIO()
        event = {'event':eventname, 'project':project.env_name, 'username':username}
        log.write_event(event)
