from datetime import datetime, timedelta
from hashlib import md5
import re

from genshi import HTML

from trac.util import datefmt
from trac.env import open_environment
from trac.mimeview.api import Context
from trac.resource import Resource
from trac.web.href import Href

from multiproject.common.projects import Project
from multiproject.core.configuration import Configuration
conf = Configuration.instance()
from multiproject.core.stubs.RequestStub import DummyReq
from multiproject.core.db import admin_query, admin_transaction
from multiproject.project.timeline import ProjectTimelineEvents


# Compiled regexp for stripping down the XML/HTML elements
re_striphtml = re.compile('<[^>]*>')

def replace_hash(matchobj):
    """ Used for filtering long git commit hash
    """
    hash = matchobj.group(0)
    return hash[:8] + '...]'


class GlobalTimeline(object):
    """ Keeps timeline events in cache and gives events either straight
    from cache or using trac interfaces
    """

    def get_latest_events(self, username, count):
        """
        Gets N amount of latest events, limited by count. If username is something else
        than "anonymous", then a special user "authenticated" is used to check for some
        permissions.

        Essentially, the events are filtered with visibility; either only public projects
        or projects that all authenticated users can see.

        :param str username: Name of the user that wants to see the event list
        :param int count: Number of maximum events to list
        :returns: List of CachedEvent objects
        """
        # Filters
        project_filters = self._get_filters_per_project(username)
        project_ids = project_filters.keys()

        # Retrieve entries within 60 days
        fromdate = datetime.now(datefmt.localtz) - timedelta(days=60)
        fromdate_sql = self._sql_date(fromdate)

        # Query for events
        events = []
        offset = 0

        with admin_query() as cursor:
            while True:
                query = "SELECT * FROM timeline_cache WHERE date > %s "
                if project_ids:
                    in_list = ','.join([str(id) for id in project_ids])
                    query += " AND project_id IN (%s)" % in_list

                # NOTE: Limit down the results but not to exact number as project_filter will decrease
                # them more and we want to end up with no less than 5 entries (see: events[:count])
                if count:
                    query += " ORDER BY date DESC LIMIT %d,%d" % (offset, count)
                else:
                    query += " ORDER BY date DESC"

                try:
                    # Wrap all events with CachedEvent, filter and add to list of events
                    cursor.execute(query, fromdate_sql)
                    rowcounter = 0

                    for event in [CachedEvent.from_sql(row) for row in cursor]:
                        rowcounter += 1
                        if event.project_id in project_filters:
                            filters = project_filters[event.project_id]
                            if event.filter in filters:
                                events.append(event)

                    # If count is set and there are more entries to find (rowcounter is full)
                    if count and (rowcounter >= count and len(events) < count):
                        offset += count

                    # Either the amount of entries is not set or we're happy with the results:
                    # Break from while loop
                    else:
                        break

                except Exception, e:
                    conf.log.exception("Listing timeline cache events failed")

        # Limit down the results
        if isinstance(count, int):
            conf.log.debug('Retrieved latest events: limit %d, found %d' % (count, len(events)))
            return events[:count]
        return events

    def get_timeline(self, fromdate, project_ids):
        """ Returns unfiltered timeline from given date for
        all projects
        """
        query = "SELECT * FROM timeline_cache WHERE date > %s"
        if project_ids:
            in_list = ','.join([str(id) for id in project_ids])
            query += " AND project_id IN (%s)" % in_list
        query += " ORDER BY date DESC"
        with admin_query() as cursor:
            try:
                cursor.execute(query, self._sql_date(fromdate))
                return [CachedEvent.from_sql(row) for row in cursor]
            except:
                conf.log.exception("Getting timeline from cache failed")

    # Timeline refreshing methods. Used for writing timeline history into database.
    def refresh_today(self, update=False):
        """
        Refresh last 24 hours for all projects

        :param bool update: Whether update the existing data or insert as new
        """
        from_date = datetime.now(datefmt.localtz) - timedelta(days=1)
        self.refresh_projects(from_date, update=update)

    def refresh_projects(self, from_date, update):
        """
        Refresh all project events from given date to this date

        :param bool update: Whether update the existing data or insert as new
        """
        to_date = datetime.now(datefmt.localtz)
        for project_identifier in self._list_project_identifiers():
            try:
                self.refresh_project(project_identifier, from_date, to_date, update=update)
            except:
                conf.log.warning("could not read %s timeline" % project_identifier)

    def refresh_project(self, project_identifier, from_date, to_date=datetime.now(datefmt.localtz),
                        afilters=None, update=False):
        """
        Will refresh a project events in cache in given date range.

        .. NOTE::

            Dates needs to be given in datefmt.localtz form

        """
        # Initialize objects
        project = Project.get(env_name=project_identifier)
        if not project:
            conf.log.warning('Project {0} is already removed from system or it cannot be found'.format(project_identifier))
            return

        e = open_environment(conf.getEnvironmentSysPath(project.env_name), use_cache=True)
        pte = ProjectTimelineEvents(e)
        providers = pte.event_providers

        project_href = Href(conf.url_projects_path + '/' + project.env_name)

        context = Context(resource=Resource(), href=project_href)
        req = self._create_dummy_req(project_identifier)
        context.req = req
        context.perm = req.perm

        # Read events from timeline
        events = []
        for provider in providers:
            try:
                # Use filters in parameter or check filters from providers
                if afilters:
                    filters = afilters
                else:
                    available_filters = provider.get_timeline_filters(req) or []
                    filters = [f[0] for f in available_filters]

                for event in provider.get_timeline_events(req, from_date, to_date, filters):
                    event_data = self._event_data(provider, event)
                    if event_data['author'] != 'trac': # Skip system events
                        events.append(CachedEvent.from_event_data(project, event_data, context, filters[0]))
            except:
                conf.log.error("Could not read timeline events for %s from %s" % (project_identifier, str(provider)))

        # Write events into sql table
        self._write_events_into_cache(events, update)

    def clean_up(self, days_to_keep=None):
        """ Clean up old events
        """
        # If no days given, we do not clean up anything
        if days_to_keep is None:
            return

        # Today in local time
        to_date = datetime.now(datefmt.localtz)
        sql_date = self._sql_date(to_date)

        # Query for deleting everything before days_to_keep from today
        query = "DELETE FROM timeline_cache WHERE date < DATE_SUB('%s', INTERVAL %s DAY)" % (sql_date, days_to_keep)
        with admin_transaction() as cursor:
            try:
                cursor.execute(query)
            except:
                conf.log.exception("Timeline cache cleanup failed")

    def remove_by_filter(self, identifier, filter):
        """ Clear out specific kind of envents by project
        """
        query = "DELETE FROM timeline_cache WHERE filter = %s AND project_identifier = %s"
        with admin_transaction() as cursor:
            try:
                cursor.execute(query, (filter, identifier))
            except:
                conf.log.exception("Failed removing items from timeline: %s, (%s,%s)" %
                                   (query, filter, identifier))

    # Internal methods
    def _get_filters_per_project(self, username):
        """
        Get same filters as the get_timeline_filters for different components would return for.

        Note: Uses a short-cut hack, not real permissions! See :method:`~GlobalTimeline._filter_for_perm`.

        :returns:
            Dictionary of sets containing timeline event filters::

                {698: set(['ticket']),
                700: set(['wiki', 'ticket'])}

        """
        filters = {}
        for project_id, value in self._get_all_user_permissions(username):
            if project_id not in filters:
                filters[project_id] = set([])
            filters[project_id] |= set(self._filter_for_perm(value))
        return filters

    def _get_all_user_permissions(self, username):
        """
        :returns:
            List of tuples, containing the project_id and permission/action::

                [(698, 'WEBDAV'),
                (698, 'XML_RPC'),
                (698, 'VERSION_CONTROL'),
                (700, 'WEBDAV'),
                (700, 'XML_RPC'),
                (700, 'VERSION_CONTROL')]

        """
        usernames = "('anonymous')"
        if username != 'anonymous':
            usernames = "('anonymous', 'authenticated')"

        # Using `project_user_visibility` table here would not be wise,
        # since it is not always up-to-date.
        query = """
SELECT DISTINCT p.project_id,a.action_string FROM action AS a
INNER JOIN group_permission AS gp ON gp.permission_key = a.action_id
INNER JOIN `group` AS g ON g.group_id = gp.group_key
INNER JOIN projects AS p ON p.trac_environment_key = g.trac_environment_key
INNER JOIN user_group AS ug ON ug.group_key = g.group_id
INNER JOIN user AS u ON u.user_id = ug.user_key
WHERE u.username IN %s
""" % usernames

        with admin_query() as cursor:
            try:
                cursor.execute(query)
                return [(row[0], row[1]) for row in cursor]
            except:
                conf.log.exception("Failed reading user permissions %s" % query)

    def _filter_for_perm(self, perm):
        # As a shortcut, we do not get filters from project but use this map based on privileges
        privilege_to_kind = {'WIKI_VIEW': 'wiki', 'DISCUSSION_VIEW': 'discussion', 'FILES_VIEW': 'files_events',
                             'FILES_DOWNLOADS_VIEW': 'files_downloads_events', 'FILES_DOWNLOADS_ADMIN': 'files_downloads_events',
                             'FILES_ADMIN': 'files_events', 'FILES_VIEW': 'files_events', 'TICKET_VIEW': 'ticket',
                             'CHANGESET_VIEW': 'changeset',
                             'MILESTONE_VIEW': 'milestone'}

        if perm in privilege_to_kind:
            return [privilege_to_kind[perm]]
        return []

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

    def _write_events_into_cache(self, events, update=False):
        for event in events:
            if update:
                event.update()
            else:
                event.save()

    def _create_dummy_req(self, project_identifier):
        uri = "%s/%s" % (conf.url_projects_path, project_identifier)
        req = DummyReq('user', 'password', 'method', uri, 'args')

        try:
            req.permissions = self._read_all_actions()
        except:
            req.permissions = []

        req.authname = 'authname'
        return req

    def _list_project_identifiers(self):
        query = "SELECT environment_name FROM projects"
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                return [row[0] for row in cursor]
            except:
                conf.log.exception("Listing all project identifiers failed")

    def _read_all_actions(self):
        query = "SELECT action_string FROM action"
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                return [row[0] for row in cursor]
            except Exception:
                conf.log.exception("Failed to read actions")

    def _sql_date(self, date):
        return date.strftime('%Y-%m-%d %H:%M:%S')


class CachedEvent(object):
    def __init__(self, fields):
        self.fields = fields
        fields['checksum'] = self._checksum()

    @staticmethod
    def from_event_data(project, event, context, filter):
        """ Factory method for creating event from event data
        """
        fields = {}
        fields['date'] = datefmt.from_utimestamp(event['dateuid'] * 1000000)
        fields['dateuid'] = event['dateuid']
        fields['kind'] = event['kind']
        fields['filter'] = filter
        fields['author'] = event['author']

        fields['project_name'] = project.project_name
        fields['project_identifier'] = project.env_name
        fields['project_id'] = str(project.id)

        # Convert rendered Markups, LazyProxies etc. into unicode
        # If event is files event, the url is not cacheable (might return 404)
        # TODO: workaround... Just accepting that in this phase.
        fields['url'] = unicode(event['render']('url', context))
        fields['description'] = unicode(event['render']('description', context))
        fields['title'] = unicode(event['render']('title', context))
        fields['summary'] = unicode(event['render']('summary', context))

        return CachedEvent(fields)

    @staticmethod
    def from_sql(row):
        """ Factory method for creating object from sql row
        """
        fields = {}
        fields['date'] = datetime.fromtimestamp(row[1], datefmt.utc)
        fields['dateuid'] = row[1]

        fields['project_id'] = row[2]
        fields['project_identifier'] = row[3]
        fields['project_name'] = row[4]
        fields['author'] = row[5]
        fields['kind'] = row[6]
        fields['filter'] = row[7]
        fields['title'] = row[8]

        fields['summary'] = row[9]
        fields['description'] = row[10]
        fields['url'] = row[11]
        fields['checksum'] = row[11]
        return CachedEvent(fields)

    def _checksum(self):
        """ Used to check if two events equals
        """
        plain = str(self.dateuid) + str(self.kind) + str(self.author)
        plain += str(self.url) + str(self.title)
        hash = md5(plain)

        # FIXME: It would be better to have this non-binary: hexdigest, but column is binary
        return hash.digest()

    def equals(self, event):
        return self.checksum == event.checksum

    def __getattr__(self, name):
        return self.fields[name]

    def render(self, field, context):
        """ Used by templates to draw event
        """
        # Previously, 'title', 'description', 'summary' fields could contain html data.
        # Currently, they are not supported.
        # I don't think that there are any HTML elements in here anymore.
        if field in ('title', 'description', 'summary'):
            return re.sub('\[[a-zA-Z0-9]{40}\]', replace_hash, self.fields[field])

        return self.fields[field]

    def save(self, replace = False):
        """ Make an sql query for inserting this record into database
        """
        # FIXME: The logic does not work as expected: if the data (ticket, for example) is changed, a new row
        # is always created.

        statement = "INSERT IGNORE"
        if replace:
            statement = "REPLACE"

        # Strip HTML elements from specified fields
        for fieldname in ('description', 'title', 'summary'):
            self.fields[fieldname] = re_striphtml.sub('', self.fields[fieldname])

        fields = 'date,dateuid,kind,filter,author,project_name,project_identifier,project_id,url,description,title,summary,checksum'
        query = statement + " INTO timeline_cache(%s) " % fields
        query += "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        with admin_transaction() as cursor:
            try:
                cursor.execute(query, (self.date, self.dateuid, self.kind, self.filter, self.author,
                                       self.project_name, self.project_identifier,
                                       self.project_id, self.url, self.description,
                                       self.title, self.summary or '', str(self.checksum)))
            except:
                conf.log.exception("Saving an event to timeline cache failed")

    def update(self):
        self.save(replace = True)
