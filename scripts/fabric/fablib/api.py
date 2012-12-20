# -*- coding: utf-8 -*-
"""
This module introduces the most commonly used classes and functions in tasks.

- PROJECT_DIR: Absolute path to project directory
- put: FileManager based put action, similar to Fabric
- get: FileManager based get action, similar to Fabric
- exists: FileManager based file exists action, similar to Fabric
- config: Configuration reader instance
- logger: Custom logger to be used when printing command states etc.

"""
__author__ = 'jumuston'


from fabric import api
from fabric import state
from fabric.state import env
from fabric.api import local

# Import classes and function to api namespace
from fablib.base import PROJECT_DIR, BUILD_DIR, SRC_DIRS, DIST_DIR, PLUGIN_DIRS, PKG_NAME
from fablib.base import Resource, TarResource, GitResource, SVNResource, TemplateResource, HTMLResourceParser
from fablib.base import get_files, get_bool_str, get_inc_version, set_version_in_file
from fablib.base import logger, config, annotate_from_sshconfig, build_join
from fablib.base import dist_join, join, rel_join, split_package_name, get_ext_path
from fablib.utils import Service, Apache, exists, get, sudo, put, run, abort


def init():
    """
    Run some initialization tasks for the lib. Needs to be called right after importing the module.
    """
    config.set_roles(api.env)

    # Replace ssh config hosts with actual names
    annotate_from_sshconfig(env)
