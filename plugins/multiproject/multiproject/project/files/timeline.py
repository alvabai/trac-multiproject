# -*- coding: utf-8 -*-
import os.path
from datetime import datetime

from genshi.builder import tag
from trac.core import Component, implements, TracError, ExtensionPoint
from trac.env import IEnvironmentSetupParticipant
from trac.util.datefmt import to_timestamp, to_datetime, utc
from trac.util.translation import _, tag_
from trac.timeline import ITimelineEventProvider

from multiproject.core.cache import EventCache
from multiproject.core.files.api import FileSystemNode, IFilesEventListener
from multiproject.core.util.filesystem import get_normalized_relative_path
from multiproject.project.files.core import FilesCoreComponent


timeline_db_version = 2


class FilesEventNotifier(Component):
    files_event_listeners = ExtensionPoint(IFilesEventListener)

    def node_created(self, username, target_node):
        for listener in self.files_event_listeners:
            listener.node_created(username, target_node)

    def node_moved(self, username, target_node, destination_node):
        for listener in self.files_event_listeners:
            listener.node_moved(username, target_node, destination_node)

    def node_copied(self, username, target_node, destination_node):
        for listener in self.files_event_listeners:
            listener.node_copied(username, target_node, destination_node)

    def node_removed(self, username, target_node):
        for listener in self.files_event_listeners:
            listener.node_removed(username, target_node)

    def node_downloaded(self, username, target_node):
        for listener in self.files_event_listeners:
            listener.node_downloaded(username, target_node)


class FilesTimelineHandler(Component):
    """ The timeline module implements timeline events.
    """
    implements(ITimelineEventProvider, IFilesEventListener)

    def __init__(self):
        self.cache = EventCache.instance()

    # ITimelineEventProvider
    def get_timeline_filters(self, req):
        if 'FILES_VIEW' in req.perm:
            yield ('files_events', _('Files events'))
        if 'FILES_DOWNLOADS_VIEW' in req.perm:
            yield ('files_downloads_events', _('Files downloads events'))

    def get_timeline_events(self, req, start, stop, filters):
        show_files_events = 'files_events' in filters
        show_downloads_events = 'files_downloads_events' in filters
        if not show_files_events and not show_downloads_events:
            return
        can_view_files = 'FILES_VIEW' in req.perm
        can_view_downloads = 'FILES_DOWNLOADS_VIEW' in req.perm
        if not can_view_files and not can_view_downloads:
            return

        type_to_can_view = {
            'download': can_view_downloads,
            'normal': can_view_files
        }
        # Get webdav events
        for event in self._get_events(start, stop, show_downloads_events and not show_files_events):
            # Return event.
            # Filter out empty parts at the same time.
            filename = os.path.basename(event['to'])
            method_parts = event['method'].split(':')

            from_path = event['from']
            path = event['to']
            if not path:
                continue
            if len(method_parts) == 3:
                method, download_str, dir_or_file = method_parts

            else:
                # Handling for old-style db data
                method, download_str, dir_or_file = (method_parts[0], 'normal',
                                                     '.' in filename and 'file' or 'dir')
                if method == 'MOVE' or method == 'COPY':
                    download_str = 'normal-normal'
                from_path = from_path.rstrip('/') if from_path else ''
                path = path.rstrip('/')

            event_time = event['time']
            author = event['author']
            try:
                if method == 'MOVE':
                    result = self.get_move_event(download_str,
                        dir_or_file, type_to_can_view, show_downloads_events, show_files_events,
                        filename, path, from_path)
                    if not result:
                        continue
                    path, event_class, title, description = result
                    yield (event_class, event_time, author, (title, description, path))
                if method == 'COPY':
                    result = self.get_copy_event(download_str,
                        dir_or_file, type_to_can_view, show_downloads_events, show_files_events,
                        filename, path, from_path)
                    if not result:
                        continue
                    path, event_class, title, description = result
                    yield (event_class, event_time, author, (title, description, path))
                elif method == 'PUT':
                    result = self.get_put_event(download_str,
                        dir_or_file, type_to_can_view, show_downloads_events, show_files_events,
                        filename, path)
                    if not result:
                        continue
                    event_class, title, description = result
                    yield (event_class, event_time, author, (title, description, path))
                elif method == 'DELETE':
                    result = self.get_delete_event(req, download_str,
                        dir_or_file, type_to_can_view, show_downloads_events, show_files_events,
                        filename, path)
                    if not result:
                        continue
                    event_class, title, description = result
                    path = ''
                    yield (event_class, event_time, author, (title, description, path))
            except TracError as e:
                self.log.warning("Invalid Files event data: %s" % (event,))

    def get_move_event(self, download_str, dir_or_file, type_to_can_view,
                         show_downloads_events, show_files_events, filename, path, from_path):
        target_path = '/' + path
        original_path = '/' + from_path
        original_type, target_type = download_str.split('-')
        can_view_original = type_to_can_view[original_type]
        can_view_target = type_to_can_view[target_type]

        if not can_view_original and not can_view_target:
            return
        elif not can_view_target:
            filename = os.path.basename(original_path)
            path = from_path

        if original_type == 'download':
            if target_type == 'download':
                if not show_downloads_events:
                    return
                event_class = 'downloadsevent-mv'
            else:
                event_class = 'downloadsevent-rm'
        elif target_type == 'download':
            event_class = 'downloadsevent-add'
        else:
            if not show_files_events:
                return
            event_class = 'filesevent-mv'

        if dir_or_file == 'dir':
            title = _("Directory %(filename)s moved", filename=filename)
            if can_view_original and can_view_target:
                description = _("Directory %(filename)s moved from %(original_path)s to %(target_path)s",
                    filename=filename, original_path=original_path, target_path=target_path)
            elif can_view_original:
                filename = os.path.basename(original_path)
                description = _("Directory %(filename)s moved from %(original_path)s",
                    filename=filename, original_path=original_path)
            else:
                description = _("Directory %(filename)s moved to %(target_path)s",
                    filename=filename, target_path=target_path)
        else:
            title = _("File %(filename)s moved", filename=filename)
            if can_view_original and can_view_target:
                description = _("File %(filename)s moved from %(original_path)s to %(target_path)s",
                    filename=filename, original_path=original_path, target_path=target_path)
            elif can_view_original:
                filename = os.path.basename(original_path)
                description = _("File %(filename)s moved from %(original_path)s",
                    filename=filename, original_path=original_path)
            else:
                description = _("File %(filename)s moved to %(target_path)s",
                    filename=filename, target_path=target_path)
        return path, event_class, title, description

    def get_copy_event(self, download_str, dir_or_file, type_to_can_view,
                       show_downloads_events, show_files_events, filename, path, from_path):
        target_path = '/' + path
        original_path = '/' + from_path
        original_type, target_type = download_str.split('-')
        can_view_original = type_to_can_view[original_type]
        can_view_target = type_to_can_view[target_type]

        if not can_view_original and not can_view_target:
            return
        elif not can_view_target:
            filename = os.path.basename(original_path)
            path = from_path

        if original_type == 'download':
            if target_type == 'download':
                if not show_downloads_events:
                    return
                event_class = 'downloadsevent-cp'
            else:
                event_class = 'filesevent-cp'
        elif target_type == 'download':
            event_class = 'downloadsevent-add'
        else:
            if not show_files_events:
                return
            event_class = 'filesevent-cp'

        if dir_or_file == 'dir':
            title = _("Directory %(filename)s copied", filename=filename)
            if can_view_original and can_view_target:
                description = _("Directory %(filename)s copied from %(original_path)s to %(target_path)s",
                    filename=filename, original_path=original_path, target_path=target_path)
            elif can_view_original:
                # No changes to the original, no event
                return
            else:
                description = _("Directory %(filename)s and its contents copied to %(target_path)s",
                    filename=filename, target_path=target_path)
        else:
            title = _("File %(filename)s moved", filename=filename)
            if can_view_original and can_view_target:
                description = _("File %(filename)s moved from %(original_path)s to %(target_path)s",
                    filename=filename, original_path=original_path, target_path=target_path)
            elif can_view_original:
                # No changes to the original, no event
                return
            else:
                description = _("File %(filename)s copied to %(target_path)s",
                    filename=filename, target_path=target_path)
        return path, event_class, title, description

    def get_put_event(self, download_str, dir_or_file, type_to_can_view,
                      show_downloads_events, show_files_events, filename, path):
        target_path = '/' + path
        target_type = download_str
        can_view_target = type_to_can_view[target_type]
        if not can_view_target:
            return
        if target_type == 'download':
            if not show_downloads_events:
                return
            event_class = 'downloadsevent-add'
        else:
            if not show_files_events:
                return
            event_class = 'filesevent-add'

        if dir_or_file == 'dir':
            title = _("Directory %(filename)s created", filename=filename)
            description = _("Directory %(filename)s created to %(target_path)s",
                filename=filename, target_path=target_path)
        else:
            if target_type == 'download':
                title = _("Download %(filename)s created", filename=filename)
                description = _("Download %(filename)s created to %(target_path)s",
                    filename=filename, target_path=target_path)
            else:
                title = _("File %(filename)s created", filename=filename)
                description = _("File %(filename)s created to %(target_path)s",
                    filename=filename, target_path=target_path)
        return event_class, title, description

    def get_delete_event(self, req, download_str, dir_or_file, type_to_can_view,
                         show_downloads_events, show_files_events, filename, path):
        target_path = '/' + path
        target_type = download_str
        can_view_target = type_to_can_view[target_type]
        if not can_view_target:
            return
        if target_type == 'download':
            if not show_downloads_events:
                return
            event_class = 'downloadsevent-rm'
        else:
            if not show_files_events:
                return
            event_class = 'filesevent-rm'

        parent_path = get_normalized_relative_path(
            'base_path_not_used', os.path.join(target_path[1:], '..'),
            assume_relative_path=True)
        if dir_or_file == 'dir':
            title = _("Directory %(filename)s deleted", filename=filename)
            description = tag_("Directory %(filename)s deleted from %(target_path)s",
                filename=filename, target_path=tag.a(target_path,
                    href=req.href.files(parent_path)))
        else:
            if target_type == 'download':
                title = _("Download %(filename)s deleted", filename=filename)
                description = tag_("Download %(filename)s deleted from %(target_path)s",
                    filename=filename, target_path=tag.a(target_path,
                        href=req.href.files(parent_path)))
            else:
                title = _("File %(filename)s deleted", filename=filename)
                description = tag_("File %(filename)s deleted from %(target_path)s",
                    filename=filename, target_path=tag.a(target_path,
                        href=req.href.files(parent_path)))
        return event_class, title, description

    def render_timeline_event(self, context, field, event):
        # Decompose event data.
        title, description, path = event[3]
        # Return apropriate content.
        if field == 'url':
            if not path:
                # method is DELETE
                return ''
            files_core = FilesCoreComponent(self.env)
            req = None
            try:
                req = context.req
            except AttributeError as e:
                pass
            download_config = files_core.files_download_config(req=req)
            node = FileSystemNode(download_config.base_path)
            node.populate_file_data(get_normalized_relative_path(node.base_path, path,
                assume_relative_path=True))
            if node.exists():
                return context.href.files(node.relative_path)
            else:
                return ""
        elif field == 'title':
            return tag(title)
        elif field == 'description':
            return tag(description)

    # Internal methods.
    def _get_events(self, start, stop, only_downloads):
        # TODO: Optimize so that if only downloads events are wanted, fetch only them
        columns = ('author', 'method', 'from', 'to')
        downloads_filter = ''
        if only_downloads:
            downloads_filter = "AND we.method LIKE '%download%'"
        sql = """SELECT  we.author, we.time, we.method, we.from, we.to
              FROM webdav_events we WHERE we.time BETWEEN %s AND %s
              {0}""".format(downloads_filter)
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        try:
            cursor.execute(sql, (to_timestamp(start), to_timestamp(stop)))
            self.log.debug(sql, start, stop)
            for row in cursor:
                yield {
                    'author': row[0],
                    'time': to_datetime(row[1], utc),
                    'method': row[2],
                    'from': row[3],
                    'to': row[4],
                }
        except Exception, e:
            self.log.exception(e)

    def node_created(self, username, target_node):
        file = self.cache.webdav(username, self.env.project_identifier,
            target_node.relative_path)
        # Ignore double put command to same file
        #(ex. when cut/paste in windows: get - put - put - delete)
        if file == target_node.relative_path:
            return

        download_or_normal = self._download_str(target_node)
        dir_or_file = 'dir' if target_node.is_dir() else 'file'
        method = 'PUT:{0}:{1}'.format(download_or_normal, dir_or_file)
        self._save_event(username, method, target_node.relative_path)

    def node_moved(self, username, target_node, destination_node):
        # Note, that the target_node relative path is put to webdav_events.from column
        download_str = '{0}-{1}'.format(self._download_str(target_node),
            self._download_str(destination_node))
        dir_or_file = 'dir' if target_node.is_dir() else 'file'
        method = 'MOVE:{0}:{1}'.format(download_str, dir_or_file)
        self._save_event(username, method, target_node.relative_path,
            destination_node.relative_path)

    def node_copied(self, username, target_node, destination_node):
        # Note, that the target_node relative path is put to webdav_events.from column
        download_str = '{0}-{1}'.format(self._download_str(target_node),
            self._download_str(destination_node))
        dir_or_file = 'dir' if target_node.is_dir() else 'file'
        method = 'COPY:{0}:{1}'.format(download_str, dir_or_file)
        self._save_event(username, method, target_node.relative_path,
            destination_node.relative_path)

    def node_removed(self, username, target_node):
        download_or_normal = self._download_str(target_node)
        dir_or_file = ''
        if target_node.is_dir():
            dir_or_file = 'dir'
        elif target_node.is_file():
            dir_or_file = 'file'
        method = 'DELETE:{0}:{1}'.format(download_or_normal, dir_or_file)
        self._save_event(username, method, target_node.relative_path)

    def _download_str(self, node):
        if node.is_download():
            return 'download'
        else:
            return 'normal'

    def _save_event(self, username, method, relative_path, to_relative_path=None):
        now = to_timestamp(datetime.now(utc))
        if to_relative_path is not None:
            moved_str = '%s'
            params = (username, now, method, relative_path, to_relative_path)
        else:
            moved_str = 'NULL'
            params = (username, now, method, relative_path)
        query = """INSERT INTO webdav_events (author, time, method, `from`, `to`)
                        VALUES (%s, %s, %s, {0}, %s)""".format(moved_str)
        @self.env.with_transaction()
        def save_event(db):
            cursor = db.cursor()
            cursor.execute(query, params)

    def node_downloaded(self, username, target_node):
        # Don't generate timeline events from
        pass


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
                module = __import__('multiproject.project.files.db.webdav_events_%s' % script_name,
                globals(), locals(), ['do_upgrade'])
                module.do_upgrade(self.env, cursor)
                db.commit()
        except:
            raise TracError("Upgrading timeline environment failed")
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
