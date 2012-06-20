import os.path

from genshi.builder import tag
from datetime import datetime, timedelta

from trac.core import ExtensionPoint, Component, implements
from trac.env import IEnvironmentSetupParticipant
from trac.mimeview import Context
from trac.wiki.formatter import format_to_oneliner
from trac.util import datefmt
from trac.util.datefmt import to_timestamp, to_datetime, utc
from trac.timeline import ITimelineEventProvider

from multiproject.common.projects import Projects
from multiproject.core.configuration import conf
from multiproject.core.path import syspath
from multiproject.core.db import trac_db_query

timeline_db_version = 1


class TimelineInformer(Component):
    """ The timeline module implements timeline events.
    """
    implements(ITimelineEventProvider)

    # ITimelineEventProvider
    def get_timeline_filters(self, req):
        if 'WEBDAV' in req.perm or 'WEBDAV_VIEW' in req.perm or 'FILE_VIEW' in req.perm:
            yield ('webdavevents', 'File events')

    def get_timeline_events(self, req, start, stop, filters):
        if 'webdavevents' not in filters or 'WEBDAV' not in req.perm:
            return

        # Create context.
        context = Context.from_request(req)
        context.realm = 'webdav-core'
        # Get webdav events
        for event in self._get_events(context, start, stop):
            # Return event.
            # Filter out empty parts at the same time.
            path_parts = [p for p in str(event['to']).split('/') if p]
            filename = ""
            if len(path_parts) > 0:
                filename = path_parts[-1]
            title = 'File or directory %s ' % filename
            if event['method'] == 'MOVE':
                title += 'moved'
                description = tag('From %s to %s' % (event['from'], event['to']))
                yield ('webdavevent-mv', event['time'], event['author'], (title, description, event['to']))
            elif event['method'] == 'PUT':
                title += 'added'
                description = tag('%s' % (event['to']))
                yield ('webdavevent-add', event['time'], event['author'], (title, description, event['to']))
            elif event['method'] == 'DELETE':
                title += 'removed'
                description = tag('%s' % (event['to']))
                yield ('webdavevent-rm', event['time'], event['author'], (title, description, event['to']))

    def render_timeline_event(self, context, field, event):
        # Decompose event data.
        title, description, path = event[3]
        # Return apropriate content.
        if field == 'url':
            if self._path_exists(context, path):
                return context.href.files(path)
            else:
                return ""
        elif field == 'title':
            return tag(title)
        elif field == 'description':
            return tag(description)

    def _path_exists(self, context, path):
        if path.startswith('/'):
            path = path[1:]
        project = conf.resolveProjectName(self.env)
        full_path = os.path.join(syspath.dav, project, path)
        return os.path.exists(full_path.encode('utf-8'))

    # Internal methods.
    def _get_events(self, context, start, stop):
        columns = ('author', 'time', 'method', 'from', 'to')
        sql = "SELECT  we.author, we.time, we.method, we.from, we.to " \
              "FROM webdav_events we WHERE we.time BETWEEN %s AND %s"
        with trac_db_query(self.env) as cursor:
            try:
                cursor.execute(sql, (to_timestamp(start), to_timestamp(stop)))
                self.log.debug(sql % (start, stop))
                for row in cursor:
                    row = dict(zip(columns, row))
                    row['time'] = to_datetime(row['time'], utc)
                    row['subject'] = format_to_oneliner(self.env, context, row['method'])
                    row['description'] = format_to_oneliner(self.env, context, row['to'])
                    yield row
            except Exception, e:
                self.log.exception(e)


class TimelineDatabaseUpgrade(Component):
    """
       Init component initialises database and environment for downloads plugin.
    """
    implements(IEnvironmentSetupParticipant)

    # IEnvironmentSetupParticipanttr
    def environment_created(self):
        db = self.env.get_db_cnx()
        self.upgrade_environment(db)

    def environment_needs_upgrade(self, db):
        cursor = db.cursor()
        # Is database up to date?
        return self._get_db_version(cursor) != timeline_db_version

    def upgrade_environment(self, db):
        self.log.debug("Upgrading timeline environment")
        cursor = db.cursor()

        # Get current database schema version
        db_version = self._get_db_version(cursor)

        # Perform incremental upgrades
        try:
            for i in range(db_version + 1, timeline_db_version + 1):
                script_name = 'db%i' % i
                module = __import__('multiproject.project.database.webdav_events_%s' % script_name,
                globals(), locals(), ['do_upgrade'])
                module.do_upgrade(self.env, cursor)
        finally:
            cursor.close()

    def _get_db_version(self, cursor):
        try:
            sql = "SELECT value FROM system WHERE name='webdav_events_version'"
            self.log.debug(sql)
            cursor.execute(sql)
            for row in cursor:
                return int(row[0])
            return 0
        except Exception, e:
            self.log.exception(e)
            return 0


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

        # end time of timeline is current time
        todate = datetime.now(datefmt.localtz)

        # start time of timeline is last update of if not known, last two monts
        prjs = Projects()
        project = prjs.get_project(env_name = conf.resolveProjectName(self.env))

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
