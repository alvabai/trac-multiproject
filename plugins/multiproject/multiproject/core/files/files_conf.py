import os
from urlparse import urlparse
from ConfigParser import NoSectionError

from trac.config import ConfigurationError
from trac.core import TracError
from trac.util import as_bool
from trac.util.translation import _

from multiproject.core.configuration import Configuration, conf
from multiproject.core.db import admin_transaction, admin_query
from multiproject.core.decorators import singleton
from multiproject.core.files.api import normalized_base_url
from multiproject.core.util import filesystem
from multiproject.core.util.filesystem import safe_path


# TODO: Move FilesDownloadConfig into files/db.py, and others to files/conf.py

@singleton
class FilesConfiguration(object):
    """
    Class for handling Files-related configurations where there are no environment available,
    like when creating a project or in webdav realm.

    See :class:`multiproject.project.files.core.FilesCoreComponent` for documentation of these
    properties. Setting downloads_dir_customizable to False improves performance.
    """

    def __init__(self):
        self.section = 'multiproject-files'
        # logic is a mapping from configuration_key to
        # tuple (default_value, value_getter, strip_value)
        _as_bool = lambda ignored_key, value: as_bool(value)
        self.logic = {
            'default_downloads_directory': ('downloads', self._get_directory, True),
            'sys_dav_root': ('/var/www/trac/webdav', self._get_abspath, True),
            'url_dav_path': ('dav', self._get_relative_url, True),
            'downloads_dir_customizable': ('True', _as_bool, True),
        }

        values = {}
        self.defaults = {}
        value = None
        options = {}
        try:
            items = Configuration.instance().config_parser.items(self.section)
            for item in items:
                options[item[0]] = item[1]
        except NoSectionError:
            options = {}

        for key, logic in self.logic.items():
            default_val, handler, do_strip = logic
            self.defaults[key] = default_val
            if key not in options:
                value = handler(key, default_val)
            else:
                value = options[key].strip() if do_strip else options[key]
                value = handler(key, value)
            values[key] = value

        self.default_downloads_directory = values['default_downloads_directory']
        self.sys_dav_root = values['sys_dav_root']
        self.url_dav_path = values['url_dav_path']
        self.downloads_dir_customizable = values['downloads_dir_customizable']

    def _get_directory(self, key, value):
        if '/' in value or '\\' in value or '..' in value:
            raise ConfigurationError('[%(section)s] %(entry)s: expected directory name, '
                                     'got %(value)s' %
                                     {'section':self.section, 'entry':key, 'value':repr(value)})
        return value

    def _get_abspath(self, key, value):
        value.rstrip('/')
        if not os.path.isabs(value):
            raise ConfigurationError('[%(section)s] %(entry)s: expected abs path, got %(value)s',
                {'section':self.section, 'entry':key, 'value':repr(value)})
        return os.path.normcase(value)

    def _get_relative_url(self, key, value):
        value = urlparse(value).path
        if not value:
            raise ConfigurationError('[%(section)s] %(entry)s: expected relative url, '
                                     'got %(value)s',
                {'section':self.section, 'entry':key, 'value':repr(value)})
        if value.strip('/') != value:
            conf.log.warning('[%(section)s] %(entry)s: value %(value)s is invalid, '
                             'it should not have leading or trailing slashes',
            {'section':self.section, 'entry':key, 'value':repr(value)})
            value = value.strip('/')
        return value

    def get_base_path(self, env_name):
        return safe_path(self.sys_dav_root, env_name)


class DownloadDirValidationException(Exception):
    """
    Raised when the Download dir to be set is not ok.
    """
    pass


class FilesDownloadConfig(object):
    """
    Class for handling 'files_downloads_dir'. It is per-project customizable
    property, stored in the system table.

    That class could be better named, and possibly moved to another place,
    but since the core/files/api.py is quite big already, decided to put it
    here.

    Once the project creation is updated so that the env is available already
    during project creation, this should be merged with the
    :class:`multiproject.project.files.core.FilesCoreComponent`.
    """
    DOWNLOADS_CACHE_TIME = 600

    def __init__(self, env_name, base_url=None):
        """
        :param env_name: valid environment name aka identifier (not validated)
        :param base_url: the base url, like '/files'
        """
        self._downloads_dir = None
        self.env_name = env_name
        files_conf = FilesConfiguration()
        self.base_path = filesystem.get_normalized_base_path(
            filesystem.safe_path(files_conf.sys_dav_root, self.env_name))
        if base_url is not None:
            self.base_url = normalized_base_url(base_url)
        else:
            self.base_url = None
        if not files_conf.downloads_dir_customizable:
            self._downloads_dir_fetched = True
            self._default = files_conf.default_downloads_directory
            self._downloads_dir = self._default
        else:
            self._downloads_dir = None
            self._downloads_dir_fetched = False
            self._default = None
        self.mc = conf.getMemcachedInstance()

    @property
    def downloads_dir(self):
        if self._downloads_dir_fetched:
            return self._downloads_dir

        self._downloads_dir_fetched = True

        new_downloads_dir = self._default
        memcache_key = None
        was_cached = True
        if new_downloads_dir is None:
            memcache_key = self._memcache_key()
            new_downloads_dir = self.mc.get(memcache_key)

        if new_downloads_dir is None:
            was_cached = False
            query = """
                SELECT value FROM `{0}`.system WHERE name = 'files_downloads_dir'
            """.format(self.env_name)
            try:
                with admin_query() as cursor:
                    cursor.execute(query)
                    for row in cursor:
                        new_downloads_dir = row[0]
            except Exception:
                conf.log.exception("Exception. Querying downloads dir failed.")
                raise TracError("Error while fetching downloads dir.")

        try:
            self._downloads_dir = self.validate_dir(new_downloads_dir)
            if not was_cached:
                self.mc.set(memcache_key, self._downloads_dir, self.DOWNLOADS_CACHE_TIME)
        except DownloadDirValidationException:
            self._downloads_dir = ''
        return self._downloads_dir

    @downloads_dir.setter
    def downloads_dir(self, new_downloads_dir):
        self._downloads_dir = self.validate_dir(new_downloads_dir)

    def reset_downloads_dir(self):
        self._downloads_dir = ''
        self.save()

    def validate_dir(self, downloads_dir):
        if not downloads_dir:
            return ''

        try:
            downloads_dir = filesystem.get_normalized_relative_path(self.base_path,
                downloads_dir, assume_relative_path=True)
        except filesystem.InvalidFilenameOrPath:
            raise DownloadDirValidationException(_('Download dir is invalid'))

        if '/' in downloads_dir or '\\' in downloads_dir:
            raise DownloadDirValidationException(_('Download directory is invalid'))
        return downloads_dir

    def save(self):
        if self._default is not None and self._default != self._downloads_dir:
            raise TracError("Downloads directory is not configurable")
        conf.log.debug("saving files_downloads_dir value %s to DB" % self._downloads_dir)
        query = """
                INSERT IGNORE INTO `{0}`.system (name, value)
                VALUES ('files_downloads_dir', %s)
                ON DUPLICATE KEY UPDATE value=VALUES(value)
        """.format(self.env_name)
        try:
            with admin_transaction() as cursor:
                cursor.execute(query, self._downloads_dir)
            self.mc.delete(self._memcache_key())
        except Exception:
            conf.log.exception("Exception. ProjectDownloadConfig save failed.")
            raise TracError("Error while saving files download information.")

    def delete(self):
        if self._default is not None:
            raise TracError("Downloads directory is not configurable")
        query = """
            DELETE FROM `{0}`.system WHERE name = 'files_downloads_dir'
        """.format(self.env_name)
        try:
            with admin_transaction() as cursor:
                cursor.execute(query)
            self.mc.delete(self._memcache_key())
        except Exception:
            conf.log.exception("Exception. ProjectDownloadConfig save failed.")
            raise TracError("Error while saving files download information.")

    def _memcache_key(self):
        return 'prj_download_dir:{0}'.format(self.env_name).encode('utf-8')
