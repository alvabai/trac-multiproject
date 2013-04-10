# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from genshi.filters.transform import Transformer
from genshi.builder import Element

from trac.core import ExtensionPoint, Component, implements
from trac.util import datefmt
from trac.util.datefmt import to_timestamp, utc
from trac.timeline import ITimelineEventProvider
from trac.web.api import ITemplateStreamFilter
from multiproject.common.projects import Project
from multiproject.core.configuration import conf


timeline_db_version = 1


class ProjectTimelineEvents(Component):
    """
      Return project timeline events
    """
    event_providers = ExtensionPoint(ITimelineEventProvider)

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
            render = lambda field, context: \
                    provider.render_timeline_event(context, field, event)
        if isinstance(date, datetime):
            dateuid = to_timestamp(date)
        else:
            dateuid = date
            date = datetime.fromtimestamp(date, utc)
        return {'kind': kind, 'author': author, 'date': date,
                'dateuid': dateuid, 'render': render, 'event': event,
                'data': data, 'provider': provider}

    def get_latest_timeline_events(self, req, count, project_created=None):
        """
        Returns latest (within 10 days) timeline events.
        If count is given, returns only given number of elements.

        :param Request req: Trac request
        :param int count: Number of elements to returns. Defaults to all
        :returns: List of events
        """
        events = []
        available_filters = []

        for event_provider in self.event_providers:
            available_filters += event_provider.get_timeline_filters(req) or []

        # TODO: make this incredibly obscure piece of code readable
        # check the request or session for enabled filters, or use default
        filters = []
        filters_list = []
        for afilter in available_filters:
            filters_list.append(afilter[0])
        filter_set = set(filters_list)
        for item in filter_set:
            filters.append(item)

        # start time of timeline is last update of if not known, last two monts
        if not project_created:
            project = Project.get(self.env)

            project_start_date = project.created
        else:
            project_start_date = project_created
        project_start_date = project_start_date.replace (tzinfo = datefmt.localtz)

        # do the actual event querying
        for provider in self.event_providers:
            todate = datetime.now(datefmt.localtz)
            fromdate = todate - timedelta(days = 10)
            eventcount = 0
            while eventcount < count and todate > project_start_date:
                for event in provider.get_timeline_events(req, fromdate, todate, filters):
                    eventcount += 1
                    events.append(self._event_data(provider, event))
                todate = fromdate
                fromdate = todate - timedelta(days = 10)
        events.sort(lambda x, y: cmp(y['date'], x['date']))

        # Note, when count = None, all the events are returned
        return events[:count] if events else []

    def get_timeline_events(self, req, time_in_days, time_in_minutes):
        conf.log.exception("Timeline.py - get timeline events")
        events = []
        available_filters = []

        for event_provider in self.event_providers:
            available_filters += event_provider.get_timeline_filters(req) or []

        # TODO: make this incredibly obscure piece of code readable
        # check the request or session for enabled filters, or use default
        filters = []
        for test in (lambda f: f[0] in req.args,
                     lambda f: len(f) == 2 or f[2]):
            if filters:
                break
            filters = [f[0] for f in available_filters if test(f)]

        # end time of timeline is current time
        todate = datetime.now(datefmt.localtz)
        fromdate = todate - timedelta(days = time_in_days, minutes = time_in_minutes)

        # do the actual event querying
        for provider in self.event_providers:
            for event in provider.get_timeline_events(req, fromdate, todate, filters):
                events.append(self._event_data(provider, event))

        events.sort(lambda x, y: cmp(y['date'], x['date']))
        return events

class TimelineEmptyMessage(Component):
    implements(ITemplateStreamFilter)

    def filter_stream(self, req, method, filename, stream, data):
        """
            Checks the project timeline and if there is no events with default params then user is
            directed to see latest events
            :param stream: Contains whole website
            :param data: Contains events, project information etc
            :return stream or if no events then redirect
        """
        if filename == 'timeline.html':
            if not data['events']:
                import datetime
                from multiproject.core.db import db_query
                project_name = data['chrome']['scripts'][0]['href'].split("/")[1]
                row = []
                with db_query(project_name) as cursor:
                    query = "SELECT MAX(t.time) FROM (SELECT time from revision UNION SELECT time from ticket UNION SELECT time FROM ticket_change UNION SELECT time FROM wiki)t;"
                    cursor.execute(query)
                    row = cursor.fetchall()
                unix_date = str(list(row)[0])
                real_unix_date = int(unix_date[1:11])
                new_date = (datetime.datetime.fromtimestamp(real_unix_date).strftime('%m/%d/%y'))
                resend_url = "../"+project_name+"/timeline?from="+new_date+"&daysback=30&authors=&wiki=on&discussion=on&ticket=on&files_events=on&files_downloads_events=on&changeset=on&milestone=on&update=Update&error=not_found"
                return req.redirect(resend_url)
        return stream
        
