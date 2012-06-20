# -*- coding: utf-8 -*-
from datetime import datetime
import json
import os

from multiproject.core.configuration import conf
from multiproject.core.analytics.dimension import UserDimension, DateDimension, \
    EventDimension, ProjectDimension, DiscussionDimension, ContextDimension
from multiproject.core.db import analytical_transaction


class ETL(object):
    """
    Base class for ETL classes.
    """

    def run(self):
        raise NotImplementedError


class EventLogETL(ETL):
    """
    Ran from cron scripts.

    .. NOTE:: Role needs to be documented better!
    """
    def __init__(self):
        self.user_dim = UserDimension()
        self.event_dim = EventDimension()
        self.project_dim = ProjectDimension()
        self.discussion_dim = DiscussionDimension()
        self.date_dim = DateDimension()
        self.context_dim = ContextDimension()

        # Extracted data transformed to sql
        self.event_insert_clause = ("INSERT IGNORE INTO event_fact VALUES(%(date_sk)d, %(project_sk)d, "
                                    "%(user_sk)d, %(event_sk)d, %(discussion_sk)d, '%(timestamp)s', %(micros)d);")
        self.request_insert_clause = ("INSERT IGNORE INTO request_fact VALUES(%(project_sk)d, %(date_sk)d, "
                                      "%(context_sk)d, %(user_sk)d, '%(timestamp)s', %(micros)d);")

        # Extract will write into these
        self.sql_rows = []

        # Progress info
        self.trans_fail_count = 0

    def run(self):
        start_time = datetime.now()
        conf.log.info("Running event ETL")

        self.transform()
        if not self.sql_rows:
            return

        if not self.load():
            conf.log.error("ETL Done. Load failed.")
            return

        end_time = datetime.now()
        conf.log.info("Event ETL done, took %s, %d rows of data inserted, %d events failed." %
                           (str(end_time - start_time), len(self.sql_rows), self.trans_fail_count))

    def consume_queue(self):
        """
        Iterates over queued unprocessed json data.
        Deletes all iterated rows.
        """
        with analytical_transaction() as cursor:
            cursor.execute('SELECT `id`, `data` FROM `data_queue`')
            rows = cursor.fetchall()
            for row in rows:
                cursor.execute('DELETE FROM data_queue WHERE id = %s', row[0])
                yield json.loads(row[1])

    def transform(self):
        """
        Convert database queue to dimensional form SQL inserts in :attr:`self.sql_rows`.
        """
        for item in self.consume_queue():
            try:
                event = self.to_event(item)
                if item['event'] == 'page_request':
                    self.sql_rows.append(self.request_insert_clause % event)
                else:
                    self.sql_rows.append(self.event_insert_clause % event)
            except Exception:
                conf.log.exception("transform failed: %s" % item)
                self.trans_fail_count += 1

    def to_event(self, log):
        """
        Transforms log row data to surrogate keys for dimensional model
        """
        # Make sure username exists
        log['username'] = log['username'] or 'anonymous'

        data = {}
        data['timestamp'] = log['timestamp']
        data['micros'] = int(log['timestamp'].split('.')[1])
        data['date_sk'] = self.date_dim.date_sk(log['timestamp'])
        data['event_sk'] = self.event_dim.event_sk(log['event'])
        data['project_sk'] = self.project_dim.project_sk(log['project'])
        data['user_sk'] = self.user_dim.user_sk(log['username'])

        # Use inapplicable sk if discussion not applicable for event
        data['discussion_sk'] = self.discussion_dim.inapplicable_sk
        if 'forum_id' in log:
            data['discussion_sk'] = self.discussion_dim.discussion_sk(log['project'], log['forum_id'])

        if log['event'] == 'page_request':
            data['context_sk'] = self.context_dim.context_sk(log['project'], log['path_info'])

        return data

    def load(self):
        """
        Load data into dimension and fact tables
        """
        try:
            return self.load_sql(self.sql_rows)
        except:
            conf.log.error("Failed to load sql")
        return False

    def dump_sql(self, sql):
        """
        Writes sql into analytics/dumps
        """
        dt = datetime.now()
        name = dt.strftime("%Y-%m-%d_%H%M%S_%f") + ".sql"
        filename = os.path.join(conf.analytics_log_file_path, "fail_dump", name)
        sql_file = None

        conf.log.error("Running data to database failed. See %s for possible errors." % filename)
        try:
            sql_file = open(filename, "w")
            sql_file.write(sql)
        except:
            conf.log.exception("Failed to open or write file %s", filename)
        finally:
            sql_file.close()

    def load_sql(self, sql_rows):
        """
        Helper method to be used for loading
        sql into analytical database.

        If sql fails we write sqldump
        """
        with analytical_transaction() as cursor:
            try:
                for row in sql_rows:
                    cursor.execute(row)
            except:
                conf.log.exception("Doing sql dump failed.")
                self.dump_sql("\n".join(sql_rows))
                # Used to return false here prior to rollback, but now we need to raise
                # the exception for the rollback to be called.
                raise

        return True


class SummaryETL(ETL):
    """
    Methods for running summaries from event fact

    Use replace if you need to re-run some period of time that
    has been summarized already. For example data failed to load so loading again
    """
    commands = {False:"INSERT IGNORE ", True:"REPLACE "}

    def __init__(self, datetime_start, datetime_end, replace = True):
        self._sql_params = {'command':self.commands[replace],
                            'dts':datetime_start.strftime("%Y-%m-%d %H:%M:%S"),
                            'dte':datetime_end.strftime("%Y-%m-%d %H:%M:%S")}

    def run_in_analytical_db(self, sql):
        try:
            with analytical_transaction() as cursor:
                cursor.execute(sql)
        except:
            conf.log.exception("Summarizing failed with sql: %s" % sql)

    def run_project_summary(self):
        project_summary = """
            %(command)s INTO project_activity_fact
            SELECT project_sk, date_sk, event_sk, HOUR(timestamp) as hour, COUNT(*) as count
            FROM event_fact
            WHERE timestamp BETWEEN '%(dts)s' AND '%(dte)s'
            GROUP BY project_sk,date_sk, event_sk, HOUR(timestamp)
        """ % self._sql_params
        self.run_in_analytical_db(project_summary)

    def run_user_summary(self):
        user_summary = """
            %(command)s INTO user_activity_fact
            SELECT user_sk, date_sk, event_sk, HOUR(timestamp) as hour, COUNT(*) as count
            FROM event_fact
            WHERE timestamp BETWEEN '%(dts)s' AND '%(dte)s'
            GROUP BY user_sk,date_sk, event_sk, HOUR(timestamp)
        """ % self._sql_params
        self.run_in_analytical_db(user_summary)

    def run_discussion_summary(self):
        discussion_summary = """
            %(command)s INTO discussion_activity_fact
            SELECT e.discussion_sk, project_sk, date_sk, event_sk, HOUR(timestamp) as hour, COUNT(*) as count
            FROM event_fact AS e
            INNER JOIN discussion_dim AS dd ON dd.discussion_sk = e.discussion_sk
            WHERE timestamp BETWEEN '%(dts)s' AND '%(dte)s' AND dd.discussion_name != '<Inapplicable>'
            GROUP BY discussion_sk, project_sk, date_sk, event_sk, HOUR(timestamp)
        """ % self._sql_params
        self.run_in_analytical_db(discussion_summary)

    def run_request_summary(self):
        request_summary = """
            %(command)s INTO request_hour_summary
            SELECT project_sk, date_sk, context_sk, user_sk, HOUR(datetime) as hour, COUNT(*) as count
            FROM request_fact
            WHERE datetime BETWEEN '%(dts)s' AND '%(dte)s'
            GROUP BY project_sk, date_sk, context_sk, user_sk, HOUR(datetime)
        """ % self._sql_params
        self.run_in_analytical_db(request_summary)

    def run_project_request_summary(self):
        project_request_summary = """
            %(command)s INTO request_project_summary
            SELECT project_sk, date_sk, context_sk, HOUR(datetime) as hour, COUNT(*) as count
            FROM request_fact
            WHERE datetime BETWEEN '%(dts)s' AND '%(dte)s'
            GROUP BY project_sk, date_sk, context_sk, HOUR(datetime)
        """ % self._sql_params
        self.run_in_analytical_db(project_request_summary)

    def run(self):
        start_time = datetime.now()

        self.run_project_summary()
        self.run_user_summary()
        self.run_discussion_summary()
        self.run_request_summary()
        self.run_project_request_summary()

        end_time = datetime.now()
        conf.log.info("Summarizing done, took %s" % str(end_time - start_time))


class SlowlyChangingDimensions(ETL):
    """ We are using SCD 2 (Slowly Changing Dimensions Type 2)

        which means that we add a new record to dimension whenever
        the record has changed in operational database

        New records are recognized with normal ETL process and
        are inserted right away. Changing records are handled like
        in the table below.

        Dimension        Maintenance
        ------------------------------
        date_dim         pre-populated
        event_dim        pre-populate manually
        project_dim      daily, SCD 2
        discussion_dim   daily, SCD 2
        user_dim         daily, SCD 2
    """
    def run(self):
        start_time = datetime.now()

        user_dim = UserDimension()
        user_dim.sync_all()

        project_dim = ProjectDimension()
        project_dim.sync_all()

        discussion_dim = DiscussionDimension()
        discussion_dim.sync_all()

        end_time = datetime.now()

        conf.log.info("SCD2 done, took %s" % str(end_time - start_time))
