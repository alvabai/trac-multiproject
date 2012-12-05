# -*- coding: utf-8 -*-
from multiproject.core import db
from multiproject.core.configuration import Configuration


class ProjectNews(object):
    """
    Class for handling data from a specific forum in discussion plugin. This is completely
    project based at the moment, so requires a trac environment upon creation.

    .. NOTE::

        We had to remove the trac Environment use from this module, because on some
        production server, opening another environment inside a wiki macro, using this
        module, caused a dead lock.
    """

    def __init__(self, env_name):
        conf = Configuration.instance()
        self.log = conf.log
        self.news_forum_name = conf.news_forum_name
        self.env_name = db.safe_string(env_name)

    def get_project_news(self, limit=0):
        """
        Return all news for a project. The data is in form of a list of dicts, containing subject,
        author, time for news post, body of the news, number of comments to the news and an
        identifier.

        :param int limit: Optional limit to limit the results
        :returns: The project news, if any
        """
        news = []

        if not limit:
            query = '''
                SELECT t.subject, t.author, t.time, t.body, COUNT(m.id), t.id
                FROM `%(database)s`.topic t
                LEFT JOIN `%(database)s`.message m ON t.id = m.topic
                INNER JOIN `%(database)s`.forum f ON t.forum = f.id
                WHERE f.name = %%s
                GROUP BY t.id
                ORDER by t.time DESC
            ''' % {'database': self.env_name}
        else:
            query = '''
                SELECT t.subject, t.author, t.time, t.body, COUNT(m.id), t.id
                FROM `%(database)s`.topic t
                LEFT JOIN `%(database)s`.message m ON t.id = m.topic
                INNER JOIN `%(database)s`.forum f ON t.forum = f.id
                WHERE f.name = %%s
                GROUP BY t.id
                ORDER by t.time DESC
                LIMIT %(limit)d
            ''' % {'limit': db.safe_int(limit),
                   'database': self.env_name}

        with db.admin_query() as cursor:
            try:
                cursor.execute(query, (self.news_forum_name,))
                for row in cursor:
                    news.append({'subject': row[0],
                                 'author': row[1],
                                 'time': row[2],
                                 'body': row[3],
                                 'num_comments': row[4],
                                 'id': row[5]})
            except Exception:
                self.log.exception("SQL query failed: %s" % query)
                raise

        return news

    def rename_news_forum(self, news_forum_name):
        """
        Renames the news forum's subject. The actual forum name cannot be changed.

        :param str news_forum_name: New name for the news forum subject
        """
        query = "UPDATE `%s`.forum SET subject = %%s WHERE name = %%s" % self.env_name

        with db.admin_transaction() as cursor:
            try:
                cursor.execute(query, (news_forum_name, self.news_forum_name))
            except Exception:
                self.log.exception("SQL query failed: %s" % query)
                raise

    def get_news_forum_id(self):
        """
        Get the database id for news forum. News forum name is defined in config.

        :returns: The database id for news forum
        """
        forum_id = None

        query = "SELECT id FROM `%s`.forum WHERE name = %%s" % self.env_name

        with db.admin_query() as cursor:
            try:
                cursor.execute(query, (self.news_forum_name,))
                row = cursor.fetchone()
                if row:
                    forum_id = row[0]
            except Exception:
                self.log.exception("SQL query failed: %s" % query)
                raise

        return forum_id
