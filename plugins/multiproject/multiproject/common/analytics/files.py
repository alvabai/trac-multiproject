# -*- coding: utf-8 -*-
"""
Analytics event tracker for Files. Listens to Files
events and saves them to database.
"""
from trac.core import Component, implements

from multiproject.core.analytics.event import EventLogIO
from multiproject.core.files.api import IFilesEventListener

class FilesAnalytics(Component):
    """
    Class handling 'file_uploaded', 'file_copied', 'file_deleted', 'file_downloaded'
    """
    implements(IFilesEventListener)

    def __init__(self):
        self.event_log = EventLogIO()

    def node_created(self, username, target_node):
        if target_node.is_file():
            self._event_write('file_uploaded', username)
            if target_node.is_download():
                self._event_write('release_uploaded', username)

    def node_moved(self, username, target_node, destination_node):
        if target_node.is_file():
            self._event_write('file_moved', username)
            if target_node.is_download():
                if destination_node.is_download():
                    self._event_write('release_moved', username)
                else:
                    self._event_write('release_deleted', username)
            elif destination_node.is_download():
                self._event_write('release_uploaded', username)

    def node_copied(self, username, target_node, destination_node):
        if target_node.is_file():
            self._event_write('file_copied', username)
            if target_node.is_download():
                if destination_node.is_download():
                    self._event_write('release_copied', username)
                # download -> file copies are file_copied events
            elif destination_node.is_download():
                self._event_write('release_uploaded', username)

    def node_removed(self, username, target_node):
        if target_node.is_file():
            self._event_write('file_deleted', username)
            if target_node.is_download():
                self._event_write('release_deleted', username)

    def node_downloaded(self, username, target_node):
        if target_node.is_file():
            self._event_write('file_downloaded', username)
            if target_node.is_download():
                self._event_write('release_downloaded', username)

    def _event_write(self, event_name, username):
        event = {
            'event': event_name,
            'project': self.env.project_identifier,
            'username': username,
            'comment': ''
        }

        try:
            self.event_log.write_event(event)
        except:
            self.log.error("FilesAnalytics._event_write(): EventLogIO.write_event failed")
