# -*- coding: utf-8 -*-
"""
This module offers a collection of wiki macros available for projects.
"""
from trac.core import Component, implements
from trac.wiki import IWikiMacroProvider
from trac.util.html import html

from multiproject.common.projects import Projects


class ProjectMacros(Component):
    """
    Component implementing few simple project based macros.
    """
    implements(IWikiMacroProvider)

    # Macros
    macros = {
        'WelcomeText': 'Display a project specific welcome test. Example: "Welcome to ProjectX"',
        'ProjectName': 'Display the name of the current project.',
        'ProjectIdentifier': 'Display the project identifier.',
        'ProjectOwner': 'Display the project owner / creator.',
        'ProjectCreateDate': 'Display the creation date of the project.',
        'ProjectUrl': 'Display url to the project.',
        'ProjectVersioncontrolUrl': 'Display url to the version control repository.',
        'ProjectWebDavUrl': 'Display url to the webdav directory for the project.'
    }

    def get_macros(self):
        """
        Returns a list of available macros.
        """
        for macro in self.macros:
            yield macro

    def get_macro_description(self, name):
        """
        Return a plain text description of the macro.

        :param str name: The name of the macro to get the description.
        """
        return self.macros.get(name)

    def expand_macro(self, formatter, name, content):
        """
        Execute / Render the macro. Return the content to caller.
        """
        if name not in self.macros:
            return None

        identifier = self.env.path.split('/')[-1]
        project = Projects().get_project(env_name=identifier)

        if project is None:
            return None

        if name == 'ProjectName':
            return project.project_name

        elif name == 'ProjectIdentifier':
            return identifier

        elif name == 'ProjectOwner':
            return project.author.username

        elif name == 'ProjectCreateDate':
            return project.created

        elif name == 'ProjectUrl':
            url = project.get_url()

            txt = content or identifier
            return html.a(txt, href = url)

        elif name == 'ProjectVersioncontrolUrl':
            url = project.get_repository_url()

            txt = content or url
            return html.a(txt, href = url)

        elif name == 'ProjectWebDavUrl':
            url = project.get_dav_url()

            txt = content or url
            return html.a(txt, href = url)

        elif name == 'WelcomeText':
            return html.h1("Welcome to " + project.project_name, id = "WelcomeToProject")
