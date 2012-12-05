# -*- coding: utf-8 -*-
"""
This module implements the UI for the home project admin, providing a way to retrieve statistics about the
projects, members and download with given filters.

Module extends the Trac admin interface for the implementation.
"""
import calendar
from datetime import datetime
import json
from operator import itemgetter

from genshi.util import plaintext
from trac.admin.api import IAdminPanelProvider
from trac.core import Component, implements
from trac.web.chrome import add_warning, add_script, add_stylesheet
from trac.util.translation import _

from multiproject.common.projects.archive import ProjectArchive
from multiproject.core.configuration import conf
from multiproject.core.db import analytical_query, admin_query, cursors
from multiproject.core.users import DATEFORMATS
from multiproject.common.projects import Projects


# Key description mapping for interesting event types
EVENT_DESCRIPTIONS = {
    'project_created':'Project created',
    'project_set_public':'Project set public',
    'project_set_private':'Project set private',
    'project_archived':'Project archived',
    'project_deleted':'Project removed',
    'wiki_edited':'Wiki pages edited',
    'topic_created':'Discussion topics created',
    'topic_edited':'Discussion topics updated',
    'topic_deleted':'Discussion topics removed',
    'message_created':'Discussion messages posted',
    'ticket_created':'Tickets created',
    'ticket_closed':'Tickets closed',
    'source_checkin':'Source updates',
    'source_checkout':'Source checkouts ',
    'file_uploaded':'Files uploaded',
    'file_downloaded':'Files downloaded',
    'release_uploaded':'Project releases uploaded',
    'release_downloaded':'Project releases downloaded',
}

class ProjectStatisticsAdminPanel(Component):
    """
    Trac admin component for project statistics: Admin > Statistics > Projects
    """
    implements(IAdminPanelProvider)

    def get_admin_panels(self, req):
        """
        Hook into admin panel by adding the Projects -section
        """
        if 'TRAC_ADMIN' in req.perm:
            yield ('statistics', _('Statistics'), 'projects', _('Projects'))

    def render_admin_panel(self, req, cat, page, path_info):
        """
        Handles the admin page requests
        """
        req.perm.require("TRAC_ADMIN")

        # Default values
        perm = 'PROJECT_VIEW'
        categories = []
        results = []
        resultsby = 'week'
        event_type = 'release_downloaded'
        maxresult_opts = [5, 10, 30, 50, 100, 0]
        maxresults = 10
        now = datetime.utcnow()
        weekday, endday = calendar.monthrange(now.year, now.month)
        starttime = datetime(year=now.year, month=now.month, day=1, hour=0, minute=0, second=0)
        endtime = datetime(year=now.year, month=now.month, day=endday, hour=23, minute=59, second=59)

        # This ain't timemachine
        if endtime > now:
            endtime = now

        # Set or reset filters back to defaults
        if 'update' in req.args.keys():
            # Try parsing the dates
            try:
                starttime = datetime.strptime(req.args.get('starttime', ''), DATEFORMATS['py'])
                endtime = datetime.strptime(req.args.get('endtime', ''), DATEFORMATS['py'])

                # Set the time to be from 00:00 -- 23:59:59
                starttime = datetime(
                    year=starttime.year,
                    month=starttime.month,
                    day=starttime.day,
                    hour=0, minute=0, second=0
                )
                endtime = datetime(
                    year=endtime.year,
                    month=endtime.month,
                    day=endtime.day,
                    hour=23, minute=59, second=59
                )

            except Exception, ex:
                self.log.warning('Date conversion failed: %s' % ex)
                add_warning(req, _('Please check the time range values as they seem inappropriate. The format is: MM/DD/YY'))

            # Set filters
            # NOTE: UI allows only one category atm
            categories_raw = req.args.get('categories', '')
            if categories_raw.strip():
                categories = [plaintext(categories_raw)]
            resultsby = req.args.get('resultsby', resultsby)

            # Get and check optional event type
            if req.args.get('event_type', '') in EVENT_DESCRIPTIONS.keys():
                event_type = req.args.get('event_type', event_type)

            # Get and check optional max results option
            maxresults = req.args.get('maxresults', maxresults)
            if isinstance(maxresults, basestring):
                maxresults = int(maxresults) if maxresults.isdigit() else 10

        # Fetch statistics: get project ids based on user rights and optional list of categories
        # NOTE: Set initial value to zero because otherwise it is considered as "fetch all"
        project_ids = [0]
        for project in Projects().get_projects_with_params(username=req.authname, perm=perm, categories=categories):
            project_ids.append(project.id)

        # Fetch project ids also from archived projects if category is not selected (archived projects no longer have one)
        if not categories:
            for archived_project in ProjectArchive().get_projects_with_params(username=req.authname, perm=perm):
                project_ids.append(archived_project.id)
        else:
            # Note about the archived project limitation
            add_warning(req, _("Archived projects are left out from statistics as they don't have category information"))

        # Fetch results either by week or project
        fetch_start = datetime.utcnow()
        if resultsby == 'project':
            results = self._get_activity_statistics_per_project(starttime, endtime, event_type, project_ids, max=maxresults)
        if resultsby == 'week':
            results = self._get_activity_statistics_per_week(starttime, endtime, event_type, project_ids, max=maxresults)

        self.log.info('Loaded statistics in %s msec' % (datetime.utcnow() - fetch_start).microseconds)

        summary = self._get_summary()

        # Calculate total
        total = sum([r['count'] for r in results])

        categories_desc = ','.join(categories) if categories else 'all'
        self.log.info('User %s is retrieving download statistics from %d projects (categories: %s), found: %d' %
                      (req.authname, len(project_ids), categories_desc, len(results)))

        # Event types, sorted by description
        event_types = sorted(EVENT_DESCRIPTIONS.items(), key=itemgetter(1))

        # Add resources
        add_script(req, 'multiproject/js/jquery-ui.js')
        add_stylesheet(req, 'multiproject/css/jquery-ui.css')
        add_stylesheet(req, 'multiproject/css/statistics.css')
        add_script(req, 'multiproject/js/raphael.js')
        add_script(req, 'multiproject/js/ico.js')
        add_script(req, 'multiproject/js/admin_analytics_projects.js')

        # Set parameters to view
        data = {
            'summary':summary,
            'perm':perm,
            'grouptypes': ['project', 'week'],
            'categories':categories,
            'resultsby':resultsby,
            'starttime':starttime,
            'endtime':endtime,
            'event_types':event_types,
            'event_type':event_type,
            'event':EVENT_DESCRIPTIONS[event_type],
            'dateformats':DATEFORMATS,
            'results':results,
            'results_json':json.dumps(results),
            'total':total,
            'categories_desc':categories_desc,
            'maxresults':maxresults,
            'maxresult_opts':maxresult_opts
        }

        return 'admin_analytics_projects.html', data


    def _get_summary(self):
        """
        Returns the summary statistics/numbers for projects::

            {'total_count':123, 'public_count':89, 'private_count':34}

        :returns: Summary in dict
        """
        query = """
        SELECT
            COUNT(p1.project_id) AS total_count,
            COUNT(p2.project_id) AS public_count
        FROM projects AS p1
        LEFT JOIN (
            SELECT project_id
            FROM projects
            WHERE published IS NOT NULL
        ) AS p2 ON p1.project_id = p2.project_id
        """
        summary = {}

        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute(query)
            summary = cursor.fetchone()

            # Calculate private number manually
            summary['private_count'] = summary['total_count'] - summary['public_count']

        return summary


    def _get_activity_statistics_per_project(self, starttime, endtime, event_type, project_ids, max=0):
        """
        Retrieves the activity statistics per each project, per each week
        Returns results in a list (one entry per each project)::

            [
                {'count':153, 'year':2012, 'week':1},
                {'count':125, 'year':2012, 'week':2},
                {'count':235, 'year':2012, 'week':3},
            ]

        :param datetime starttime: Start time of the query
        :param datetime endtime: End time of the query
        :param str event_type:
            Name of event type to fetch statistics from.
            See :py:data:`multiproject.home.admin.analytics.EVENT_DESCRIPTIONS`
        :param list project_ids: Optional list of project ids to limit down the results
        :param int max: Optional limiter of max entries. Zero means no limit (default)
        :returns:
            Result list, containing dict entry for each week. Data also may contain some project info, but that is
            no to be trusted.
        :rtype: list

        """
        projects = []
        results = []
        startstr = starttime.strftime('%Y-%m-%d')
        endstr = endtime.strftime('%Y-%m-%d')

        # Find out the project ids that actually have data (instead of iterating all the projects)
        fquery = '''
        SELECT
            pd.project_key AS id,
            pd.identifier AS identifier,
            pd.project_name AS name,
            ef.event_sk AS event_sk
        FROM project_dim AS pd
        LEFT JOIN event_fact AS ef ON ef.project_sk = pd.project_sk
        WHERE
            pd.project_key IN ({0}) AND
            ef.timestamp >= %s AND
            ef.timestamp <= %s AND
            ef.event_sk = (
                SELECT  event_sk
                FROM  event_dim
                WHERE action_name =  %s
            )
        GROUP BY pd.project_key
        '''.format(','.join([str(pi) for pi in project_ids]))


        with analytical_query(cursors.DictCursor) as cursor:
            cursor.execute(fquery, (starttime, endtime, event_type))
            projects = [row for row in cursor]

        self.log.debug('Provided %d project ids, found %d interesting ones' % (len(project_ids), len(projects)))

        # SQL query for retrieving weekly statistics
        query = '''
        SELECT
            COUNT(ef.event_sk) AS count,
            ef.event_sk,
            dd.week AS week,
            dd.year AS year,
            DATE_FORMAT(dd.date, '%%Y-%%m-%%d') AS date
        FROM event_fact AS ef
        RIGHT JOIN (
          SELECT
            date, week, year, date_sk
          FROM date_dim
          WHERE
           date_dim.date >= DATE(%s)
           AND date_dim.date <= DATE(%s)
        )
        AS dd ON dd.date_sk = ef.date_sk
        LEFT JOIN project_dim AS pd ON pd.project_sk = ef.project_sk
        WHERE (
          ef.event_sk = %s OR
          ef.event_sk IS NULL
        )
        {0}
        GROUP BY dd.week
        ORDER BY dd.date ASC
        '''

        # Open cursor that we'll be used for reading different tables
        with analytical_query(cursors.DictCursor) as cursor:

            # Iterate each project to fetch and group weekly results per project
            for project in projects:
                # Retrieve statistics for each week, for the specified only
                qwhere = 'AND (pd.project_key = %d OR pd.project_sk IS NULL)' % project['id']
                cursor.execute(query.format(qwhere), (startstr, endstr, project['event_sk']))
                presults = [row for row in cursor]

                # Update project dict with additional info like download counts per project
                project['weeks'] = presults
                project['count'] = sum([r['count'] for r in presults])

                results.append(project)

        # Sort the results based on project count key (as it cannot be be done in SQL)
        results = sorted(results, key=itemgetter('count'), reverse=True)

        # Limit down the top results if wanted
        if max:
            results = results[:max]

        return results


    def _get_activity_statistics_per_week(self, starttime, endtime, event_type, project_ids=None, max=0):
        """
        Retrieves the download statistics per each week, without making separation between the projects
        Returns results in a list (one entry per each week)::

            [
                {'count':153, 'year':2012, 'week':1},
                {'count':125, 'year':2012, 'week':2},
                {'count':235, 'year':2012, 'week':3},
            ]

        :param datetime starttime: Start time of the query
        :param datetime endtime: End time of the query
        :param str event_type:
                    Name of event type to fetch statistics from.
                    See :py:data:`multiproject.home.admin.analytics.EVENT_DESCRIPTIONS`
        :param list project_ids: Optional list of project ids to limit down the results
        :param int max: Optional limiter of max entries. Zero means no limit (default)
        :returns:
            Result list, containing dict entry for each week. Data also may contain some project info, but that is
            no to be trusted.
        :rtype: list

        """
        qwhere = ''
        startstr = starttime.strftime('%Y-%m-%d')
        endstr = endtime.strftime('%Y-%m-%d')

        # Optional limit for specified projects
        if project_ids:
            qwhere = 'AND (pd.project_key IN (%s) OR pd.project_sk IS NULL)' % ','.join([str(int(pid)) for pid in project_ids])

        query = '''
        SELECT
            COUNT(ef.event_sk) AS count,
            pd.project_sk AS id,
            pd.project_name AS name,
            pd.identifier AS identifier,
            ef.event_sk,
            dd.week AS week,
            dd.year AS year,
            DATE_FORMAT(dd.date, '%%Y-%%m-%%d') AS date
        FROM event_fact AS ef
        RIGHT JOIN (
          SELECT
            date, week, year, date_sk
          FROM date_dim
          WHERE
           date_dim.date >= DATE(%s)
           AND date_dim.date <= DATE(%s)
        )
        AS dd ON dd.date_sk = ef.date_sk
        LEFT JOIN project_dim AS pd on pd.project_sk = ef.project_sk
        WHERE (
          ef.event_sk = (
            SELECT  event_sk
            FROM  event_dim
            WHERE action_name =  %s
          )
          OR ef.event_sk IS NULL
        )
        {0}
        GROUP BY dd.week
        ORDER BY dd.date ASC
        '''.format(qwhere)

        results = []

        with analytical_query(cursors.DictCursor) as cursor:
            cursor.execute(query, (startstr, endstr, event_type))
            results = [row for row in cursor]

        # Sort the results based on project count key (as it cannot be be done in SQL)
        if max:
            # Take top results but keep still the date order
            results = sorted(results, key=itemgetter('count'), reverse=True)
            results = results[:max]
            results = sorted(results, key=itemgetter('date'))

        return results


class MemberStatisticsAdminPanel(Component):
    """
    Trac admin component for member statistics: Admin > Statistics > Members
    """
    implements(IAdminPanelProvider)

    def get_admin_panels(self, req):
        """
        Hook into admin panel by adding the Members -section
        """
        if 'TRAC_ADMIN' in req.perm:
            yield ('statistics', _('Statistics'), 'members', _('Members'))

    def render_admin_panel(self, req, cat, page, path_info):
        """
        Handles the admin page requests
        """
        req.perm.require("TRAC_ADMIN")

        # Default values
        perm = 'TRAC_ADMIN'
        stat_types = [('activity', 'Activity'), ('registration', 'Registrations')]
        stat_type = 'registration'
        maxresult_opts = [5, 10, 30, 50, 100, 0]
        maxresults = 10
        now = datetime.utcnow()
        weekday, endday = calendar.monthrange(now.year, now.month)
        starttime = datetime(year=now.year, month=now.month, day=1, hour=0, minute=0, second=0)
        endtime = datetime(year=now.year, month=now.month, day=endday, hour=23, minute=59, second=59)

        # This ain't timemachine
        if endtime > now:
            endtime = now

        # Set or reset filters back to defaults
        if 'update' in req.args.keys():
            # Try parsing the dates
            try:
                starttime = datetime.strptime(req.args.get('starttime', ''), DATEFORMATS['py'])
                endtime = datetime.strptime(req.args.get('endtime', ''), DATEFORMATS['py'])

                # Set the time to be from 00:00 -- 23:59:59
                starttime = datetime(
                    year=starttime.year,
                    month=starttime.month,
                    day=starttime.day,
                    hour=0, minute=0, second=0
                )
                endtime = datetime(
                    year=endtime.year,
                    month=endtime.month,
                    day=endtime.day,
                    hour=23, minute=59, second=59
                )

            except Exception, ex:
                self.log.warning('Date conversion failed: %s' % ex)
                add_warning(req, _('Please check the time range values as they seem inappropriate. The format is: MM/DD/YY'))

            # Set filters
            # NOTE: UI allows only one category atm
            categories_raw = req.args.get('categories', '')
            if categories_raw.strip():
                categories = [plaintext(categories_raw)]

            maxresults = req.args.get('maxresults', maxresults)
            stat_type = req.args.get('stat_type', stat_type)

            # If maxresults does not seem num
            if isinstance(maxresults, basestring):
                maxresults = int(maxresults) if maxresults.isdigit() else 10


        # Fetch statistics and summary
        results = []
        if stat_type == 'activity':
            results = self._get_members_activity(starttime, endtime, max=maxresults)
        elif stat_type == 'registration':
            results = self._get_members_registrations(starttime, endtime, max=maxresults)

        summary = self._get_summary()

        # Add resources
        add_script(req, 'multiproject/js/jquery-ui.js')
        add_stylesheet(req, 'multiproject/css/jquery-ui.css')

        # Set parameters to view
        data = {
            'summary':summary,
            'perm':perm,
            'stat_type':stat_type,
            'stat_name':dict(stat_types)[stat_type],
            'stat_types':stat_types,
            'starttime':starttime,
            'endtime':endtime,
            'dateformats':DATEFORMATS,
            'results':results,
            'maxresults':maxresults,
            'maxresult_opts':maxresult_opts
        }

        return 'admin_analytics_members.html', data


    def _get_summary(self):
        """
        Returns the summary statistics/numbers for members::

            {'total_count':123, 'active_count':89, 'passive_count':34}

        :returns: Summary in dict
        """
        active_within_months = 2
        query = """
        SELECT
            COUNT(u1.user_id) AS total_count,
            COUNT(u2.user_id) AS active_count
        FROM user AS u1
        LEFT JOIN (
            SELECT user_id
            FROM user
            WHERE last_login > NOW() - INTERVAL %s MONTH
        ) AS u2 ON u1.user_id = u2.user_id
        """
        summary = {}

        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute(query, active_within_months)
            summary = cursor.fetchone()

            # Calculate passive number manually
            summary['passive_count'] = summary['total_count'] - summary['active_count']

        return summary


    def _get_members_activity(self, starttime, endtime, max=0):
        """
        Implements the query: fetch most active (based on user_activity information) users

        :param datetime starttime: Start time of the query
        :param datetime endtime: End time of the query
        :param int max: Optional limiter of max entries. Zero means no limit (default)
        :returns: List of members, ordered by activity
        :rtype: list
        """
        results = []

        qlimit = 'LIMIT %d' % max if max else ''

        query = """
        SELECT
            CONVERT(SUM(ua.count), SIGNED INTEGER) AS count,
            ud.user_key AS id,
            ud.username AS username,
            ud.givenName AS given_name,
            ud.mail AS mail,
            u.last_login AS last_login,
            ud.lastName AS last_name
        FROM user_activity_fact AS ua
        LEFT JOIN user_dim AS ud ON ud.user_sk = ua.user_sk
        LEFT JOIN date_dim AS dd ON dd.date_sk = ua.date_sk
        LEFT JOIN {0}.user AS u ON u.user_id = ud.user_key
        WHERE (dd.date >= %s AND dd.date <= %s)
        GROUP BY ud.user_key
        ORDER BY count DESC
        {1}
        """.format(conf.db_admin_schema_name, qlimit)

        # Fetch all the projects using time range only
        with analytical_query(cursors.DictCursor) as cursor:
            cursor.execute(query, (starttime, endtime))
            for row in cursor:
                results.append(row)

        return results


    def _get_members_registrations(self, starttime, endtime, max=0):
        """
        Implements the query: fetch users created between selected time range

        :param datetime starttime: Start time of the query
        :param datetime endtime: End time of the query
        :param int max: Optional limiter of max entries. Zero means no limit (default)
        :returns:
            List of members, ordered by activity::

                [{'id':123, 'username':'john', 'givenName':'John', 'mail':'john.doe@company.com',
                'last_login':<timestamp>, 'created':<datetime>, 'lastName':'Doe'}, {'id':'...'}]

        :rtype: list
        """
        results = []

        qlimit = 'LIMIT %d' % max if max else ''

        query = """
        SELECT
            u.user_id AS id,
            u.username AS username,
            u.givenName AS given_name,
            u.mail AS mail,
            u.last_login AS last_login,
            u.created AS created,
            u.lastName AS last_name
        FROM user AS u
        WHERE (u.created >= %s AND u.created <= %s)
        ORDER BY u.created DESC
        {1}
        """.format(conf.db_admin_schema_name, qlimit)

        # Fetch all the projects using time range only
        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute(query, (starttime, endtime))
            for row in cursor:
                results.append(row)

        return results

