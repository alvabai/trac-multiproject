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

    def get_latest_timeline_events(self, req, count):
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
        for test in (lambda f: f[0] in req.args,
                     lambda f: len(f) == 2 or f[2]):
            if filters:
                break
            filters = [f[0] for f in available_filters if test(f)]

        # start time of timeline is last update of if not known, last two monts
        project = Project.get(self.env)

        project_start_date = project.created
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
        if filename == 'timeline.html':
            if not data['events']:
                return stream | Transformer('//form[@id="prefs"]').before(Element('p')('No events match your search criteria, change the parameters and try again'))
        return stream
