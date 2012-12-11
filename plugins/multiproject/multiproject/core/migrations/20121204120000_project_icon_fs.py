# -*- coding: utf-8 -*-
"""

"""
import os
from hashlib import md5
import Image, ImageFile

from multiproject.core.db import admin_query, cursors, admin_transaction
from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.configuration import DimensionOption, conf


class ProjectIcons2FS(MigrateBase):
    """
    Dumps the project icons blobs into filesystem
    """
    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = self.__doc__
        self.icon_dir = conf.get('multiproject-projects', 'icon_dir')
        self.projects_dir = conf.get('multiproject', 'sys_projects_root')
        self.content_types = {
            'image/png': 'png',
            'image/jpeg': 'jpeg',
            'image/jpg': 'jpeg',
        }

        # Parse option value using custom Trac option:
        value = conf.get('multiproject-projects', 'icon_size', '64x64')
        self.icon_size = DimensionOption(section=None, name=None)._parse_dimension(value)

        icon_width = 64
        icon_height = 64

    def upgrade(self):
        """
        Run DB upgrade steps
        """
        if self.applied():
            return True

        if self.icon_dir and not os.path.exists(self.icon_dir):
            os.makedirs(self.icon_dir)

        # Load default icon
        default_icon_path = ''
        sql_default_icon = 'SELECT icon_data, content_type FROM project_icon WHERE icon_id = %s'
        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute(sql_default_icon, conf.default_icon_id or 0)
            row = cursor.fetchone()
            if row:
                image_path = os.path.join(self.icon_dir or '/tmp', 'project_default_icon.%s' % self.content_types[row['content_type']])
                self._save_image(row['icon_data'], image_path)
                self.printout('Saved default image: %s' % image_path)
                self.printwarn('Set icon_default_url = <url> in configuration', 'TODO')

        # Load each project icon data and dump them to filesystem
        sql_projects = '''
        SELECT p.project_id AS id, p.icon_id, i.icon_data, i.content_type, te.identifier
        FROM projects AS p
        LEFT JOIN project_icon AS i ON i.icon_id = p.icon_id
        LEFT JOIN trac_environment AS te ON te.environment_id = p.trac_environment_key
        '''
        project_icons = {}

        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute(sql_projects)
            for row in cursor.fetchall():
                # If icon is set
                if row['icon_id'] is not None:
                    try:
                        hash = md5()
                        hash.update(row['icon_data'])
                        image_name = '%s-%s.%s' % (row['id'], hash.hexdigest(), self.content_types[row['content_type']])
                        image_path = os.path.join(self.projects_dir, row['identifier'], 'htdocs', image_name)

                        # Use custom icon dir if set
                        if self.icon_dir:
                            image_path = os.path.join(self.icon_dir, image_name)

                        try:
                            self._save_image(row['icon_data'], image_path)
                        except IOError, err:
                            self.printerr('Failed to save image: %s. Please fix before continue' % err)
                            return

                        self.printout('Save project image: %s' % image_path)
                        project_icons[row['id']] = image_name

                    except KeyError:
                        self.printerr('Unsupported image format: %s. Please fix before continue' % row['content_type'])
                        return

        # Remove / add columns
        self.printok('Found %d projects with icons' % len(project_icons), 'NOTE')

        with admin_transaction() as cursor:
            cursor.execute('ALTER TABLE projects DROP COLUMN `icon_id`')
            cursor.execute('DROP TABLE project_icon')
            cursor.execute('ALTER TABLE `projects` ADD COLUMN `icon_name` varchar(50) DEFAULT NULL AFTER `parent_id`')

            for pid, image_name in project_icons.items():
                cursor.execute('UPDATE projects SET icon_name = %s WHERE project_id = %s', (image_name, pid))

        # No actual migration steps to run, just check the column exists so that we'll pass the migration successfully
        queries = ['SELECT icon_name FROM projects']
        return self.manager.db_upgrade(queries)

    def downgrade(self):
        """
        Do downgrade steps.

        .. WARNING::

            This does not restore the data, only the tables.

        """
        if not self.applied():
            return False

        queries = [
            'ALTER TABLE projects DROP COLUMN `icon_name`',
            'ALTER TABLE `projects` ADD COLUMN `icon_id` int(10) unsigned DEFAULT NULL AFTER `parent_id`',
            '''CREATE TABLE `project_icon` (
              `icon_id` int(11) NOT NULL AUTO_INCREMENT,
              `icon_data` blob NOT NULL,
              `content_type` varchar(64) COLLATE utf8_bin NOT NULL,
              PRIMARY KEY (`icon_id`)
            ) ENGINE=InnoDB'''
        ]
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
        # Read and parse the given icon size
        icon_width = self.icon_size['width']
        icon_height = self.icon_size['height']

        # Create image from data
        with open(path, 'w+b') as fd:
            p = ImageFile.Parser()
            p.feed(data)

            try:
                img = p.close()
                # Resize images if needed, and force them to specified size
                img.thumbnail((icon_width, icon_height), Image.ANTIALIAS)
                img = img.convert("RGBA")
                img = img.transform((icon_width, icon_height), Image.EXTENT, (0, 0, icon_width, icon_height))
                img.save(path)

            except IOError, err:
                self.printerr('Failed to create image %s, skipping it (%s)' % (path, err))


MigrateMgr.instance().add(ProjectIcons2FS())
