from multiproject.core.configuration import Configuration
conf = Configuration.instance()
from multiproject.core.db import admin_query, safe_int


class CQDEWatchlistStore(object):
    """ DAO for project watchlists
    """

    def __init__(self):
        # TODO cache some database results
        #self.__cache = WatchlistCache.instance()
        self.notifications = [
            "immediate",
            "daily",
            "weekly",
            "none"
        ]

    def watch_project(self, user_id, project_id, notification="immediate"):
        user_id = safe_int(user_id)
        project_id = safe_int(project_id)

        if notification not in self.notifications:
            notification = self.notifications[0]

        with admin_query() as cursor:
            try:
                cursor.callproc("watch_project", [user_id, project_id, notification])
            except:
                conf.log.exception("Failed to add project %d into user's %d watch list" %
                                   (project_id, user_id))

    def unwatch_project(self, user_id, project_id):
        user_id = safe_int(user_id)
        project_id = safe_int(project_id)

        with admin_query() as cursor:
            try:
                cursor.callproc("unwatch_project", [user_id, project_id])
            except:
                conf.log.exception("Failed to remove project %d from user's %d watch list" %
                                   (project_id, user_id))

    def get_projects_by_user(self, user_id):
        user_id = safe_int(user_id)

        watched_projects = []
        with admin_query() as cursor:
            try:
                query = "SELECT * FROM watchlist WHERE user_key = %s"
                cursor.execute(query, user_id)

                for row in cursor:
                    p = Watch.from_sql_row(row)
                    watched_projects.append(p)
            except:
                conf.log.exception("Exception: Watchlist: get_projects_by_user query failed.")

        return watched_projects

    def get_watchers_by_project(self, project_id):
        project_id = safe_int(project_id)

        watched_projects = []
        with admin_query() as cursor:
            try:
                query = "SELECT * FROM watchlist WHERE project_key = %s"
                cursor.execute(query, project_id)

                for row in cursor:
                    p = Watch.from_sql_row(row)
                    watched_projects.append(p)
            except:
                conf.log.exception("Exception: Watchlist: get_watchers_by_project query failed.")

        return watched_projects

    def is_watching(self, user_id, project_id):
        if user_id:
            watchlist = self.get_projects_by_user(user_id)
            for item in watchlist:
                if item.project_id == project_id:
                    return True
        return False

    def get_by_notification(self, notification):
        if notification not in self.notifications:
            notification = self.notifications[0]

        watched_projects = []
        with admin_query() as cursor:
            try:
                query = "SELECT * FROM watchlist WHERE notification = %s"
                cursor.execute(query, notification)

                for row in cursor:
                    p = Watch.from_sql_row(row)
                    watched_projects.append(p)
            except:
                conf.log.exception("Exception: Watchlist: get_by_notification query failed.")

        return watched_projects


class Watch(object):
    """ Class for database Watchlist entities
    """

    def __init__(self):
        self.user_id = None
        self.project_id = None
        self.notification = None

    @staticmethod
    def from_sql_row(row):
        """ Static factory method
        """
        w = Watch()
        w.user_id = row[0]
        w.project_id = row[1]
        w.notification = row[2]
        return w

    def __repr__(self):
        return "<Watch:" + str(self.user_id) + ":" + str(self.project_id) + ":" + str(self.notification) + ">"
