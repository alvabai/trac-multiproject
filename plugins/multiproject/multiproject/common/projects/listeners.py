# -*- coding: utf-8 -*-
"""
Module contains the project related listener interfaces that should be implemented
by the components that are interested in project changes. Example::

    from multiproject.common.projects.listeners import IProjectChangeListener

    class MyProjectListener(Component):
        change_listeners = ExtensionPoint(IProjectChangeListener)

        def project_created(self, project):
            self.log.info('Project %s created' %s project)

:py:class:`Project object <multiproject.common.projects.api.Project>` is provided as a parameter.
It contains valuable information like:

- id
- env_name
- project_name
- author_id
- created
- trac_environment_key


.. NOTE::

    If you're only interested in Trac environment creation,
    there is: :py:class:`trac.env.IEnvironmentSetupParticipant`

"""
from trac.core import Interface


class IProjectChangeListener(Interface):
    """
    Extension point interface for components that require notification
    when project are created, modified, or deleted.
    """

    def project_created(project):
        """
        Called when a project is created. Only argument `project` is
        a dictionary with download field values.

        :param Project project: Created project
        """
        pass

    def project_set_public(project):
        """
        Called when a project is set public. Only argument `project` is
        a dictionary with download field values.

        :param Project project: Published project
        """
        pass

    def project_set_private(project):
        """
        Called when a project is set private. Only argument `project` is
        a dictionary with download field values.

        :param Project project: Hidden project
        """
        pass

    def project_archived(project):
        """
        Called when a project is archived. Only argument `project` is
        a dictionary with download field values.

        :param Project project: Archived project
        """
        pass

    def project_deleted(project):
        """
        Called when a project is deleted. Only argument `project` is
        a dictionary with download field values.

        :param Project project: Deleted project

        .. IMPORTANT::

            Delete project object is given, but the project database and Trac environment are already deleted
            at this point.

        """
        pass

    def project_watched(project):
        """
        Called when a project is followed.
        """
        pass