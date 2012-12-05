# -*- coding: utf-8 -*-
"""
Project activity updater.
"""
from datetime import datetime, timedelta

from trac.env import open_environment
from trac.util import datefmt
from trac.timeline.web_ui import TimelineModule

from multiproject.core.configuration import Configuration
from multiproject.core.stubs.RequestStub import DummyReq
from multiproject.core.db import admin_query, admin_transaction


class ActivityCalculator(object):
    """
    Class for updating project activity
    """

    def __init__(self):
        self.conf = Configuration.instance()

    def update_project_activity(self, project_name=''):
        """
        Updates project_activity table with timeline activities, that took
        place in past 60 days (or configured with key
        multiproject.activity_calculation_daterange)

        .. NOTE::

            This is a heavy operation. This should not be done in a request,
            especially if done for all projects.

        :param str project_name: If given, only the given project is updated
        """
        with admin_query() as cursor:
            try:
                query = "SELECT project_id, environment_name FROM projects"

                if project_name:
                    query += " WHERE environment_name = %s"
                    cursor.execute(query, (project_name,))
                else:
                    cursor.execute(query)

                for row in cursor:
                    # create trac Environment object for current project
                    try:
                        tracenviron = open_environment(
                            self.conf.getEnvironmentSysPath(row[1]), use_cache=True)
                        events = self._get_timeline_events(tracenviron)
                        self._update_timeline_events(tracenviron, events, row[0])
                    except Exception:
                        self.conf.log.warning('Failed to load project (id: %s) - skipping it' % row[0])

            except Exception:
                self.conf.log.exception("Failed to update project activity")
                raise

    def _get_timeline_events(self, tracenviron):
        """
        Get the timeline events for one project, based on the given in trac
        environment object.
        """

        # skip empty projects
        if tracenviron is None:
            return None

        daterange = int(self.conf.activity_calculation_daterange)

        # end time of timeline is current time
        todate = datetime.now(datefmt.localtz)

        # start time of timeline is last update of if not known, last two monts
        fromdate = todate
        fromdate = fromdate - timedelta(days=daterange)

        stop = todate
        start = fromdate

        # events will continue the timeline events
        events = []

        # Access event providers for timeline events
        event_providers = TimelineModule(tracenviron).event_providers

        # create a dummy request (see class above)
        req = DummyReq('user', 'password', 'method', 'uri', 'args')
        req.permissions = ('TICKET_VIEW', 'CHANGESET_VIEW', 'WIKI_VIEW', 'ATTACHMENT_VIEW', 'DISCUSSION_VIEW')
        req.authname = 'authname'

        # filters will contain the available timeline event types
        available_filters = []
        for event_provider in event_providers:
            available_filters += event_provider.get_timeline_filters(req) or []

        filters = []
        # check the request or session for enabled filters, or use default
        for test in (lambda f: f[0] in req.args,
                     lambda f: len(f) == 2 or f[2]):
            if filters:
                break
            filters = [f[0] for f in available_filters if test(f)]

        # do the actual event querying
        for provider in event_providers:
            # note: this is because if discussion is not in current project, do not fail
            try:
                for event in provider.get_timeline_events(req, start, stop, filters):
                    events.append(self._event_data(provider, event))
            except Exception:
                self.conf.log.exception(
                    "ActivityCalculator.get_timeline_events(%s) couldn't get timeline events from %s." %
                    (tracenviron.project_name, str(provider)))

        events.sort(lambda x, y: cmp(y['date'], x['date']))

        return events

    def _update_timeline_events(self, tracenviron, events, project_id):
        """
        Update the given project events into project_activity table.
        """
        # sum up the events by source (ticket, wiki, scm)
        ticket_changes = wiki_changes = scm_changes = attachment_changes = discussion_changes = 0

        ticket_kinds = ['newticket', 'reopenedticket', 'closedticket', 'editedticket']
        wiki_kinds = ['wiki']
        scm_kinds = ['changeset']
        attachment_kinds = ['attachment']
        dibo_kinds = ['newforum', 'newtopic', 'newmessage']

        #ticket:2|wiki:2|scm:5|attachment:1|discussion:1
        ticket_factor = float(self.conf.get_activity_factor('ticket'))
        wiki_factor = float(self.conf.get_activity_factor('wiki'))
        scm_factor = float(self.conf.get_activity_factor('scm'))
        attachment_factor = float(self.conf.get_activity_factor('attachment'))
        discussion_factor = float(self.conf.get_activity_factor('discussion'))

        daterange = int(self.conf.activity_calculation_daterange)

        for event in events:
            kind = event['kind']
            now = datetime.now(datefmt.localtz)
            days = now - event['date']
            days_old = float(days.days + 1)
            if days_old == 0:
                days_old = 1
            date_factor = float(daterange / days_old)
            if kind in ticket_kinds:
                ticket_changes += (date_factor * ticket_factor)
            elif kind in wiki_kinds:
                wiki_changes += (date_factor * wiki_factor)
            elif kind in scm_kinds:
                scm_changes += (date_factor * scm_factor)
            elif kind in attachment_kinds:
                attachment_changes += (date_factor * attachment_factor)
            elif kind in dibo_kinds:
                discussion_changes += (date_factor * discussion_factor)

        self.conf.log.debug("Updating project %s activity: ticket_changes: %d, wiki_changes: %d, "
                            "scm_changes: %d, attachment_changes: %d, discussion_changes: %d" %
                            (tracenviron.project_name, ticket_changes, wiki_changes, scm_changes,
                             attachment_changes, discussion_changes))

        with admin_transaction() as cursor:
            query = '''
                UPDATE project_activity
                    SET ticket_changes = %s,
                        wiki_changes = %s,
                        scm_changes = %s,
                        attachment_changes = %s,
                        discussion_changes = %s,
                        last_update = NOW(),
                        project_description = %s
                WHERE project_key = %s
            '''
            cursor.execute(query, (ticket_changes, wiki_changes, scm_changes, attachment_changes,
                                   discussion_changes, tracenviron.project_description, project_id))

            if cursor.rowcount == 0:
                query = '''
                    INSERT INTO project_activity
                        SET project_key = %s,
                            ticket_changes = %s,
                            wiki_changes = %s,
                            scm_changes = %s,
                            attachment_changes = %s,
                            discussion_changes = %s,
                            last_update = NOW(),
                            project_description = %s
                '''
                cursor.execute(query, (project_id, ticket_changes, wiki_changes, scm_changes,
                                       attachment_changes, discussion_changes, tracenviron.project_description))

    # FIXME: is this needed at all for our needs?
    def _event_data(self, provider, event):
        """Compose the timeline event date from the event tuple and prepared
        provider methods"""
        if len(event) == 6: # 0.10 events
            kind, url, title, date, author, markup = event
            data = {'url': url, 'title': title, 'description': markup}
            render = lambda field, context: data.get(field)
        else: # 0.11 events
            if len(event) == 5: # with special provider
                kind, date, author, data, provider = event
            else:
                kind, date, author, data = event
            render = lambda field, context:\
            provider.render_timeline_event(context, field, event)
        if isinstance(date, datetime):
            dateuid = datefmt.to_timestamp(date)
        else:
            dateuid = date
            date = datetime.fromtimestamp(date, datefmt.utc)
        return {'kind': kind, 'author': author, 'date': date,
                'dateuid': dateuid, 'render': render, 'event': event,
                'data': data, 'provider': provider}
