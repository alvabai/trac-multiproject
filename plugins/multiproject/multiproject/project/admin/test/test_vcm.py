#!/usr/bin/env python
# coding: utf-8

"""Tests for package vcm. 
"""

import sys
import os
import unittest2 as unittest

from mock import patch
from mock import sentinel
from mock import MagicMock as Mock

sys.path.append(
    os.path.normpath(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
    )
)


class TestGetRepositories(unittest.TestCase):

    mock = Mock()
    @patch.dict('sys.modules', {
        'multiproject': mock,
        'multiproject.core': mock.core,
        'multiproject.core.configuration': mock.core.configuration, 

        'multiproject.common': mock.common,
        'multiproject.common.projects': mock.common.projects,
        'multiproject.common.projects.commands': mock.common.projects.commands,
        'multiproject.common.projects.project': mock.common.projects.project,

        'multiproject.project': mock.project,
        'multiproject.project.admin': mock.project.admin,
        })
    def setUp(self):
        from multiproject.core.configuration import conf
        from vcm import RepositoriesAdminPanel
        RepositoriesAdminPanel.env = Mock()
        from trac.core import ComponentManager
        mgr = ComponentManager()
        self.rap = RepositoriesAdminPanel(mgr)

    def test_return_type(self):
        val = self.rap.get_repositories()
        self.assertTrue(list == type(val))


if __name__ == "__main__":
    unittest.main()

# vim: sw=4

