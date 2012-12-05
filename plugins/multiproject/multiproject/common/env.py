# -*- coding: utf-8 -*-
import os

from trac.core import implements, Component
from trac.env import IEnvironmentSetupParticipant
from trac.web import Href


class MultiProjectEnvironmentInit(Component):
    """
    Component, which makes sure that Environment has the following
    attributes after the environment is created and checked for upgrade:

        - ``env.home_href``
        - ``env.abs_home_href``
        - ``env.project_identifier``, str like 'home' or 'projectX'
        - ``env._abs_href``

    The actual work is done in the environment_needs_upgrade method.

    The following attributes, which uses the ``env._abs_href``, are affected:

        - ``env.href``
        - ``env.abs_href``

    The following configuration variables should be set in [multiproject]:

        - ``url_projects_path``
        - ``sys_home_project_name``
        - ``domain_name``
        - ``default_http_scheme``

    """
    implements(IEnvironmentSetupParticipant)

    def environment_created(self):
        self.environment_needs_upgrade(None)

    def environment_needs_upgrade(self, db):
        url_projects_path = self.env.config.get('multiproject', 'url_projects_path', '')
        url_projects_path = url_projects_path.rstrip('/')
        home_path = '{0}/{1}'.format(url_projects_path,
            self.env.config.get('multiproject', 'sys_home_project_name', 'home'))
        self.env.project_identifier = env_name = os.path.split(self.env.path)[-1]
        env_path = '{0}/{1}'.format(url_projects_path, env_name)
        self.env.home_href = Href(home_path)

        domain_name = self.env.config.get('multiproject', 'domain_name', '')
        if not domain_name:
            self.env.abs_home_href = self.env.home_href
            self.env._abs_href = Href(env_path)
        else:
            default_http_scheme = self.env.config.get('multiproject',
                'default_http_scheme', 'https')
            url_service = '{0}://{1}'.format(default_http_scheme, domain_name)
            self.env.abs_home_href = Href('{0}{1}'.format(
                url_service, home_path))
            self.env._abs_href = Href('{0}{1}'.format(
                url_service, env_path))
        return False

    def upgrade_environment(self, db):
        pass
