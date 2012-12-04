# -*- coding: utf-8 -*-
"""

"""
from hashlib import md5
import Image, ImageFile

from multiproject.core.db import admin_query, cursors
from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.configuration import conf


class ProjectIcons2FS(MigrateBase):
    """
    Dumps the project icons blobs into filesystem
    """
    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = self.__doc__
        self.icon_dir = conf.get('multiproject-projects', 'icon_dir')
        self.content_types = {
            'image/png': 'png',
            'image/jpeg': 'jpeg',
            'image/jpg': 'jpeg',
        }

    def upgrade(self):
        """
        Create two ssh related tables into trac_admin database.
        """
        if self.applied():
            return True

        # Load default icon
        default_icon_path = ''
        sql_default_icon = 'SELECT icon_data, content_type FROM project_icon WHERE icon_id = %s'
        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute(sql_default_icon, conf.default_icon_id or 0)
            row = cursor.fetchone()
            if row:
                image_path = '/tmp/project_default_icon.%s' % self.content_types[row['content_type']]
                self._save_image(row['icon_data'], image_path)
                print 'Default image: %s' % image_path

        # Load each project icon data and dump them to filesystem
        sql_projects = '''
        SELECT p.project_id AS id, p.icon_id, i.icon_data, i.content_type, te.identifier
        FROM projects AS p
        LEFT JOIN project_icon AS i ON i.icon_id = p.icon_id
        LEFT JOIN trac_environment AS te ON te.environment_id = p.trac_environment_key
        '''

        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute(sql_projects)
            for row in cursor.fetchall():
                # If icon is set
                if row['icon_id'] is not None:
                    try:
                        hash = md5()
                        hash.update(row['icon_data'])
                        image_path = '/tmp/%s-%s.%s' % (row['id'], hash.hexdigest(), self.content_types[row['content_type']])
                        print 'Project image: %s' % image_path
                        self._save_image(row['icon_data'], image_path)
                    except KeyError:
                        print 'Unsupported image format: %s' % row['content_type']

        #

        queries = []
        return self.manager.db_upgrade(queries)

    def downgrade(self):
        """
        Remove the ssh keys related tables from trac_admin database.
        """
        if not self.applied():
            return False

        # Umm actually, this is a bad idea I think...
        queries = []
        return self.manager.db_downgrade(queries)

    def applied(self):
        """
        Check if migration is already applied or not
        :returns: True if migrated, otherwise False
        """
        # Test if icon_id column still exists: Exception = migration already applied
        with admin_query() as cursor:
            try:
                cursor.execute('SELECT icon_id FROM projects')
            except Exception:
                return True

        return False

    def _save_image(self, data, path):

        # Create image from data
        with open(path, 'w+b') as fd:
            p = ImageFile.Parser()
            p.feed(data)

            try:
                img = p.close()
                img.thumbnail((64, 64), Image.ANTIALIAS)
                img.save(path)
            except IOError, err:
                print 'Failed to create image %s, skipping it (%s)' % (path, err)

            #img = Image.open(fd)
            #img.thumbnail((64, 64), Image.ANTIALIAS)


MigrateMgr.instance().add(ProjectIcons2FS())


