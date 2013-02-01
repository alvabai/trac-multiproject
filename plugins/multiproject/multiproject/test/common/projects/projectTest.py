# -*- coding: utf-8 -*-
class ProjectStub(object):

    FIELDS = {
        'id': 'project_id',
        'project_name': 'project_name',
        'env_name': 'environment_name',
        'description': 'description',
        'author_id': 'author',
        'created': 'created',
        'updated': 'updated',
        'published': 'published',
        'parent_id': 'parent_id',
        'icon_name': 'icon_name',
        'trac_environment_key': 'trac_environment_key'
    }
    FIELD_COUNT = len(FIELDS)

    def __init__(self, id, env_name, project_name, description, author_id, created, trac_environment_key=None, public=False,
                 updated=None, published=None, parent_id=None,
                 discforum=False, icon_name=None, priority=None):

        # Private attributes for properties
        self._parent_project = None
        self._author = None
        self.description = description

        # NOTE: id is None when new project is created
        self.id = int(id) if id else None
        self.env_name = env_name
        self.project_name = project_name
        self.created = created
        self.author_id = int(author_id)
        self.parent_id = int(parent_id) if parent_id else None

        # Only None in case project is not recorded into database yet.
        # Avoid using, migrate to `self.id` everywhere.
        self.trac_environment_key = trac_environment_key

        self.updated = updated
        self.published = published
        self.discforum = discforum
        self.icon_name = icon_name
        self.priority = priority
        self.public = public

    def project_name(self):
        """
        Property for getting project name
        """
        return self._name.decode('utf-8')
    
    def project(self):
        """
            Returns projects visibility True : False
        """
        return self.public