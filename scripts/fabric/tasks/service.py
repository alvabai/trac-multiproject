# -*- coding: utf-8 -*-
'''
Contents of this module
'''
from datetime import datetime, timedelta
import calendar
import re

__author__ = 'jumuston'

from fabric.api import task

from fablib.api import logger, run
from fablib.utils import DatabaseManager


@task
def show_summary():
    """
    Shows summary about the setup
    """
    logger.info(run('echo ROOT=$ROOT'))


@task
def show_projects_count():
    """
    Show the number of registered projects
    """
    dbm = DatabaseManager('trac_admin')
    sql = 'SELECT COUNT(*) FROM projects\G'
    output = dbm.run(sql, re.compile(r': (\d+)'))

    logger.info('Projects: %s' % output)


@task
def show_users_count():
    """
    Show the number of registered users
    """
    dbm = DatabaseManager('trac_admin')
    sql = 'SELECT COUNT(*) FROM user\G'
    output = dbm.run(sql, re.compile(r': (\d+)'))

    logger.info('Users: %s' % output)

@task
def show_active_users_count(month='', year=''):
    """
    Show the number of users logged in within 3months
    """
    # NOTE: Fabric parameters are always strings
    # Get the month's
    now = datetime.utcnow()
    month = int(month) if month else now.month
    year = int(year) if year else now.year

    weekday, endday = calendar.monthrange(year, month)
    start_date = datetime(year=year, month=month, day=1, hour=0, minute=0, second=0)
    end_date = datetime(year=year, month=month, day=endday, hour=23, minute=59, second=59)

    startstr = start_date.strftime('%Y-%m-%d %H:%M:%S')
    endstr = end_date.strftime('%Y-%m-%d %H:%M:%S')

    dbm = DatabaseManager('trac_admin')
    sql = '''
    SELECT COUNT(*)
    FROM user
    WHERE
        last_login >= TIMESTAMP('%s')
    AND
        last_login <= TIMESTAMP('%s')\G
    ''' % (startstr, endstr)

    output = dbm.run(sql, re.compile(r': (\d+)'))
    logger.info('Date range: %s - %s ' % (startstr, endstr))
    logger.info('Active users: %s' % output)


@task
def show_projects_downloads(month='', year=''):
    """
    Show the number of downloads done within selected month
    """
    # NOTE: Fabric parameters are always strings
    # Get the month's start and end date
    now = datetime.utcnow()
    month = int(month) if month else now.month
    year = int(year) if year else now.year

    weekday, endday = calendar.monthrange(year, month)
    start_date = datetime(year=year, month=month, day=1, hour=0, minute=0, second=0)
    end_date = datetime(year=year, month=month, day=endday, hour=23, minute=59, second=59)

    startstr = start_date.strftime('%Y-%m-%d %H:%M:%S')
    endstr = end_date.strftime('%Y-%m-%d %H:%M:%S')

    dbm = DatabaseManager('trac_analytical')
    sql = '''
    SELECT COUNT(*)
    FROM event_fact AS ef
    WHERE
        event_sk = (
            SELECT event_sk
            FROM event_dim
            WHERE action_name = 'release_downloaded'
        )
    AND
        ef.timestamp >= TIMESTAMP('%s')
    AND
        ef.timestamp <= TIMESTAMP('%s')\G
    ''' % (startstr, endstr)

    output = dbm.run(sql, re.compile(r': (\d+)'))

    logger.info('Date range: %s - %s ' % (startstr, endstr))
    logger.info('Project downloads: %s' % output)


@task
def show_projects_top_downloads(month='', year='', limit='50'):
    """
    Show the number of downloads done within selected month

    Example query::

        fab -H hostname service.show_projects_top_downloads
        fab -H hostname service.show_projects_top_downloads:month=10
        fab -H hostname service.show_projects_top_downloads:month=9,year=2011,limit=10

    """
    # NOTE: Fabric parameters are always strings
    # Get the month's start and end date
    now = datetime.utcnow()
    month = int(month) if month else now.month
    year = int(year) if year else now.year

    weekday, endday = calendar.monthrange(year, month)
    start_date = datetime(year=year, month=month, day=1, hour=0, minute=0, second=0)
    end_date = datetime(year=year, month=month, day=endday, hour=23, minute=59, second=59)

    startstr = start_date.strftime('%Y-%m-%d %H:%M:%S')
    endstr = end_date.strftime('%Y-%m-%d %H:%M:%S')

    dbm = DatabaseManager('trac_analytical')
    sql = '''
    SELECT project_dim.project_name AS Project, COUNT(*) AS Downloads
    FROM event_fact, project_dim
    WHERE event_sk = (
        SELECT event_sk
        FROM event_dim
        WHERE action_name = 'release_downloaded'
    )
    AND (
        timestamp >= TIMESTAMP('%(startdate)s')
    AND
        timestamp < TIMESTAMPADD(MONTH, 1, '%(startdate)s')
    )
    AND project_dim.project_sk = event_fact.project_sk
    GROUP BY event_fact.project_sk
    ORDER BY Downloads DESC
    LIMIT %(limit)s;
    ''' % dict(startdate=startstr, limit=limit)

    output = dbm.run(sql)

    logger.info('Date range: %s - %s ' % (startstr, endstr))
    logger.info('Top %s downloads:\n %s' % (limit, output))


@task
def show_projects_top_weekly_downloads(week='', year='', limit='50'):
    """
    Show the number of downloads done within selected week

    Example query::

        fab -H hostname service.show_projects_top_downloads
        fab -H hostname service.show_projects_top_downloads:week=10
        fab -H hostname service.show_projects_top_downloads:week=9,year=2011,limit=10

    """
    # NOTE: Fabric parameters are always strings
    # Get the month's start and end date
    now = datetime.utcnow()
    # isocalendar returns tuple year, week, weekday
    week = int(week) if week else now.isocalendar()[1]
    year = int(year) if year else now.year

    first_day = datetime(year=year,month=1,day=1)

    # If first day is > Thu, next week is the first week
    if first_day.isoweekday() > 4:
        first_day = first_day + timedelta(days=7-first_day.weekday())
    else:
        first_day = first_day - timedelta(days=first_day.weekday())

    start_date = first_day + timedelta(weeks=week-1)
    end_date = start_date + timedelta(weeks=1)

    startstr = start_date.strftime('%Y-%m-%d %H:%M:%S')
    endstr = end_date.strftime('%Y-%m-%d %H:%M:%S')

    dbm = DatabaseManager('trac_analytical')
    sql = '''
    SELECT project_dim.project_name AS Project, COUNT(*) AS Downloads
    FROM event_fact, project_dim
    WHERE event_sk = (
        SELECT event_sk
        FROM event_dim
        WHERE action_name = 'release_downloaded'
    )
    AND (
        timestamp >= TIMESTAMP('%(startdate)s')
    AND
        timestamp < TIMESTAMPADD(WEEK, 1, '%(startdate)s')
    )
    AND project_dim.project_sk = event_fact.project_sk
    GROUP BY event_fact.project_sk
    ORDER BY Downloads DESC
    LIMIT %(limit)s;
    ''' % dict(startdate=startstr, limit=limit)

    output = dbm.run(sql)

    logger.info('Date range: week %s, %s - %s ' % (str(week), startstr, endstr))
    logger.info('Top %s downloads:\n %s' % (limit, output))


@task
def project_downloaders(from_date='', to_date='', projects=''):
    """
    Get list user emails that have downloaded from a project within given time.

    Example query::

        fab -H hostname "service.project_downloaders:from_date=2011-07-01,to_date=2011-12-31,projects=foo;bar"

    Note the date YYYY-MM-DD
    """
    for param in (from_date, to_date):
        if not re.match(r'\d{4}-\d{2}-\d{2}', param):
            print 'Argument %s is not a valid date' % param
            return

    # split from ; and quote with ''
    projects = projects.split(';')
    print 'Projects: %s' % ', '.join(projects)
    projects = ["'%s'" % p for p in projects]

    sql = '''
    SELECT user_dim.mail FROM event_fact, user_dim
    WHERE event_fact.event_sk = (
        SELECT event_sk
        FROM event_dim
        WHERE action_name
        LIKE 'release_downloaded'
    )
    AND event_fact.user_sk = user_dim.user_sk
    AND event_fact.user_sk NOT IN (
        SELECT user_sk FROM user_dim
        WHERE username IN ('anonymous', '<Inapplicable>')
    )
    AND user_dim.mail != ''
    AND event_fact.project_sk IN (
        SELECT DISTINCT project_sk FROM project_dim WHERE identifier in (%(projects)s)
    )
    AND event_fact.timestamp >= TIMESTAMP('%(from_date)s 0:0:0')
    AND event_fact.timestamp < TIMESTAMP('%(to_date)s 23:59:59')

    GROUP BY user_dim.user_sk;
    ''' % {'from_date': from_date, 'to_date': to_date, 'projects': ','.join(projects) }

    dbm = DatabaseManager('trac_analytical')
    output = dbm.run(sql)

    print output
