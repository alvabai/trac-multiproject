from datetime import datetime

from trac.util.datefmt import to_timestamp, utc

from multiproject.core.cache.event_cache import EventCache
from multiproject.core.configuration import conf
from multiproject.core.db import db_transaction
from multiproject.core.analytics.event import EventLogIO


class TimelineEvent(object):
    """ CQDE time line actions used by files.py and dav_access.py

        Available webdav events:
         PUT      = A new file
         MKCOL    = A new directory -> forced to use PUT event
         DELETE   = Removing a file or a directory
         MOVE     = Moving a file or a directory
         GET      = (not used)
         PROPFIND = (not used)
    """

    def __init__(self, project, username):
        self.cache = EventCache.instance()
        self.user = username
        self.project = project

    def _get_file(self, filename):
        """
        Get's rid of the filename's first two folders, when filename is an absolute path.
        For example, "///path/to" and "/xxx/yyy/path/to" will become "path/to"

        This is because webdav events are reported as "/dav/identifier/path/to".
        """
        # TODO: change so that the '/dav/identifier/' part is removed already in webdav / files
        return filename.split('/',3)[3]

    def _save(self, query, params):
        with db_transaction(self.project) as cursor:
            try:
                cursor.execute(query, params)
            except:
                conf.log.exception("Cannot save webdav event")

    def _event(self, method, filename):
        timenow = to_timestamp(datetime.now(utc))
        query = """
        INSERT INTO webdav_events (author, time, method, `from`, `to`)
             VALUES (%(user)s, %(timenow)s, %(method)s, NULL,
             %(filename)s)"""
        self._save(query, {'user': self.user, 'timenow': timenow, 'method':method, 'filename':self._get_file(filename)})
        self._write_eventlog(method)

    def _move_event(self, filenew, fileold):
        timenow = to_timestamp(datetime.now(utc))
        query = """
        INSERT INTO webdav_events (author, time, method, `from`, `to`)
             VALUES (%(user)s, %(timenow)s, %(method)s,
             %(fileold)s,
             %(filenew)s)"""
        self._save(query, {'user': self.user, 'timenow': timenow, 'method':'MOVE',
                           'fileold': self._get_file(fileold),
                           'filenew': self._get_file(filenew)})
        self._write_eventlog('MOVE')

    def webdav_event(self, req, destination_path=None):
        if req.method == 'MOVE':
            if destination_path:
                self._move_event(destination_path, req.uri)
        elif req.method == 'COPY':
            if destination_path:
                # TODO: implement copy operation event log
                self._event('PUT', self._get_file(destination_path))
        elif req.method == 'PUT':
            file = self.cache.webdav(self.user, self.project, req.uri)
            # Ignore double put command to same file
            #(ex. when cut/paste in windows: get - put - put - delete)
            if file != req.uri:
                self._event("PUT", req.uri)
        elif req.method == 'MKCOL':
            self._event("PUT", req.uri)
        else:
            self._event(req.method, req.uri)

    def filestab_event(self, eventtype, filename):
        if eventtype in ("PUT", "DELETE"):
            self._event(eventtype, filename)

    def _write_eventlog(self, method):
        log = EventLogIO()
        event = {}
        event_name = ''
        if method == "PUT": # A new file
            event_name = 'file_uploaded'
        elif method == "DELETE": # Removing a file or a directory
            event_name = 'file_deleted'
        elif method == "MOVE": # Moving a file or a directory
            event_name = 'file_moved'
        elif method == "MKCOL":  # A new directory
            return
        else:       # unsupported method
            conf.log.warning("TimelineEvent._write_eventlog(): unsupported method '" + method + "'")
            return

        event['event'] = event_name
        event['project'] = self.project
        event['username'] = self.user
        event['comment'] = 'Action via WEBDAV'
        try:
            log.write_event(event)
        except:
            conf.log.error("TimelineEvent._write_eventlog(): EventLogIO.write_event failed")
